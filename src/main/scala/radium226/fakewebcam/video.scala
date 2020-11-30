package radium226.fakewebcam.video

import radium226.fakewebcam.Frame
import java.nio.file.Path

import _root_.io.chrisdavenport.log4cats.slf4j.Slf4jLogger
import cats.effect.{Blocker, Concurrent, ContextShift, Resource, Sync}
import fs2._
import cats.implicits._
import cats.effect.implicits._
import fs2.io.readInputStream
import fs2.text.{lines, utf8Decode}
import radium226.fakewebcam.mediainfo.MediaInfo

case class Video(filePath: Path)

trait VideoAlgebra[F[_]] {

  def readFramesFromVideo(video: Video, mediaInfo: MediaInfo): Stream[F, Frame]

}

object VideoAlgebra {

  val ChunkSize = 512

  def algebra[F[_]: Sync: ContextShift: Concurrent](blocker: Blocker): Resource[F, VideoAlgebra[F]] = Resource.liftF(Slf4jLogger.fromName[F]("camera").map({ logger => new VideoAlgebra[F] {

    override def readFramesFromVideo(video: Video, mediaInfo: MediaInfo): Stream[F, Frame] = {
      val ffmpegCommand = List("ffmpeg",
        //"-loglevel", "quiet",
        "-i", s"${video.filePath}",
        "-f", "rawvideo",
        "-s", s"${mediaInfo.frameSize.width}x${mediaInfo.frameSize.height}",
        "-vcodec", "rawvideo",
        //"-filter:v", s"fps=fps=10",
        "-pix_fmt", "bgr24",
        "-f", "rawvideo",
        "-"
      )
      /*  "ffmpeg",
        //"-loglevel", "quiet",
        "-f", "v4l2",
        "-input_format", PixelFormat.format(camera.mediaInfo.pixelFormat),
        "-framerate", s"${camera.mediaInfo.framePerSecond.value}",
        "-video_size", s"${camera.mediaInfo.frameSize.width}x${camera.mediaInfo.frameSize.height}",
        "-i", s"${camera.devicePath}",
        "-c:v", "rawvideo",
        "-an",
        "-f", "image2pipe",
        "-s", s"${camera.mediaInfo.frameSize.width}x${camera.mediaInfo.frameSize.height}",
        "-pix_fmt", "bgr24",
        "-"
      )*/

      val ffmpegProcessBuilder = new ProcessBuilder()
        .inheritIO()
        .redirectInput(ProcessBuilder.Redirect.INHERIT)
        .redirectError(ProcessBuilder.Redirect.PIPE)
        .redirectOutput(ProcessBuilder.Redirect.PIPE)
        .command(ffmpegCommand: _*)

      Stream
        .eval[F, Process](F.delay(ffmpegProcessBuilder.start()))
        .flatMap({ ffmpegProcess =>
          val errorStream = readInputStream(F.delay(ffmpegProcess.getErrorStream), ChunkSize, blocker)
            .through(utf8Decode[F])
            .through(lines[F])
            .evalMap({ line => logger.info(line) })
            .drain

          val outputStream = readInputStream[F](F.delay(ffmpegProcess.getInputStream), ChunkSize, blocker)

          outputStream concurrently errorStream
        })
        .chunkN((3 * mediaInfo.frameSize.width * mediaInfo.frameSize.height).toInt, allowFewer = false)
        .zipWithIndex
        .map({ case (byteChunk, index) =>
          //if (index % 25 == 0) println(s"index=${index}")
          Frame(mediaInfo.frameSize, byteChunk.toBitVector.toByteArray)
        })
    }

  }}))

}

trait VideoSyntax {

  implicit class VideoOps(video: Video) {

    def readFrames[F[_]]: Stream[F, Frame] = ???

  }

}

object syntax extends VideoSyntax