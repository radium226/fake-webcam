package radium226.fakewebcam.fakecamera

import java.nio.file.{Path, Paths}

import io.chrisdavenport.log4cats.slf4j.Slf4jLogger
import cats._
import cats.effect._
import fs2._
import fs2.io._
import radium226.fakewebcam.Frame
import cats.implicits._
import cats.effect.implicits._
import fs2.Chunk.ByteVectorChunk
import fs2.text.{lines, utf8Decode}
import radium226.fakewebcam.mediainfo.{FramePerSecond, MediaInfo}

object V4L2LoopbackFakeCameraAlgebra {

  def algebra[F[_]: Sync: ContextShift: Concurrent](blocker: Blocker): Resource[F, FakeCameraAlgebra[F]] = {

    val loggerF = Slf4jLogger.fromName[F]("fakeCamera")

    Resource.liftF(loggerF).map({ logger =>
      new FakeCameraAlgebra[F] {

        def insertModule(label: String): F[Unit] = {
          F.delay({
            val modprobeCommand = List(
              "sudo", "modprobe", "v4l2loopback",
              "devices=1",
              s"card_label=${label}",
              "exclusive_caps=1"
            )

            val modprobeProcessBuilder = new ProcessBuilder()
              .inheritIO()
              .command(modprobeCommand: _*)

            val modprobeProcess = modprobeProcessBuilder.start()
            modprobeProcess.waitFor()
          }).void
        }

        def removeModule(): F[Unit] = {
          F.delay({
            val modprobeCommand = List("sudo", "modprobe", "--remove", "v4l2loopback")

            val modprobeProcessBuilder = new ProcessBuilder()
              .inheritIO()
              .command(modprobeCommand: _*)

            val modprobeProcess = modprobeProcessBuilder.start()
            modprobeProcess.waitFor()
          }).void
        }

        override def fakeCameraResource(label: String): Resource[F, FakeCamera] = {
          Resource
            .make[F, Unit](insertModule(label))({ _ => removeModule() })
            .as(FakeCamera(label, Paths.get("/dev/video0")))

        }
/*
ffmpeg \
        -re \
        -f "rawvideo" \
        -video_size "1280x720" \
        -pixel_format "bgr24" \
        -framerate 30 \
        -i pipe:- \
        -vcodec "rawvideo" \
        -pix_fmt "yuv420p" \
        -threads "0" \
        -f "v4l2" \
        "/dev/video2"
 */
        override def writeFramesToFakeCamera(fakeCamera: FakeCamera, mediaInfo: MediaInfo): Pipe[F, Frame, Unit] = { frameStream =>
          val ffmpegCommand = List(
            "ffmpeg",
            "-loglevel", "quiet",
            //"-re",
            "-f", "rawvideo",
            "-video_size", s"${mediaInfo.frameSize.width}x${mediaInfo.frameSize.height}",
            "-pixel_format", "bgr24",
            "-framerate", s"${mediaInfo.framePerSecond.value}",
            "-i", "-",
            "-vcodec", "rawvideo",
            "-pix_fmt", "yuv420p",
            "-threads", "0",
            "-f", "v4l2",
            s"${fakeCamera.devicePath}"
          )

          val ffmpegProcessBuilder = new ProcessBuilder()
            .inheritIO()
            .redirectInput(ProcessBuilder.Redirect.PIPE)
            .redirectOutput(ProcessBuilder.Redirect.PIPE)
            .redirectError(ProcessBuilder.Redirect.PIPE)
            .command(ffmpegCommand: _*)

          Stream
            .eval[F, Process](F.delay(ffmpegProcessBuilder.start()))
            .flatMap({ ffmpegProcess =>
              val chunkSize = 512

              val inputStream = frameStream
                .flatMap({ frame =>
                  Stream.chunk(Chunk.bytes(frame.bytes))
                })
                .through(writeOutputStream[F](F.delay(ffmpegProcess.getOutputStream), blocker))

              val outputStream = readInputStream[F](F.delay(ffmpegProcess.getInputStream), chunkSize, blocker)
                .through(utf8Decode[F])
                .through(lines[F])
                .evalMap({ line => logger.info(line) })
                .drain

              val errorStream = readInputStream[F](F.delay(ffmpegProcess.getErrorStream), chunkSize, blocker)
                .through(utf8Decode[F])
                .through(lines[F])
                .evalMap({ line => logger.info(line) })
                .drain

              inputStream concurrently outputStream concurrently errorStream
            })
        }
      }
    })
  }

}

trait FakeCameraAlgebra[F[_]] {

  def fakeCameraResource(label: String): Resource[F, FakeCamera];

  def writeFramesToFakeCamera(fakeCamera: FakeCamera, mediaInfo: MediaInfo): Pipe[F, Frame, Unit]

}

trait FakeCameraSyntax {

  implicit class FakeCameraOps(fakeCamera: FakeCamera) {

    def writeFrames[F[_]: FakeCameraAlgebra](mediaInfo: MediaInfo): Pipe[F, Frame, Unit] = F.writeFramesToFakeCamera(fakeCamera, mediaInfo)

  }

}

case class FakeCamera(label: String, devicePath: Path)

object syntax extends FakeCameraSyntax