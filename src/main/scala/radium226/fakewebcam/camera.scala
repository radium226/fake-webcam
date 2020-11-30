package radium226.fakewebcam
package camera

import java.nio.file.Path

import io.chrisdavenport.log4cats.slf4j.Slf4jLogger
import cats.effect.{Blocker, Concurrent, ContextShift, Resource, Sync}
import radium226.fakewebcam.mediainfo.{MediaInfo, MediaInfoAlgebra, PixelFormat}
import cats.implicits._
import fs2._
import fs2.io._
import fs2.text._


object CameraAlgebra {

  def apply[F[_]](implicit cameraAlgebra: CameraAlgebra[F]): CameraAlgebra[F] = cameraAlgebra

  def algebra[F[_]: Sync: Concurrent: ContextShift](blocker: Blocker, mediaInfoAlgebra: MediaInfoAlgebra[F]): Resource[F, CameraAlgebra[F]] = {

    Resource.liftF(Slf4jLogger.fromName[F]("camera").map({ logger =>
      new CameraAlgebra[F] {

        val ChunkSize = 4096

        import mediainfo.syntax._

        override def makeCamera(devicePath: Path): Stream[F, Camera] = {
          mediaInfoAlgebra
            .probeMediaInfo(devicePath)
            .map({ mediaInfo => Camera(devicePath, mediaInfo)})
        }

        override def readFramesFromCamera(camera: Camera): Stream[F, Frame] = {
            val ffmpegCommand = List("ffmpeg",
              //"-re",
              "-loglevel", "quiet",
              "-f", "v4l2",
              "-i", s"${camera.devicePath}",
              "-f", "rawvideo",
              "-vcodec", "rawvideo",
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
              .chunkN((3 * camera.mediaInfo.frameSize.width * camera.mediaInfo.frameSize.height).toInt, allowFewer = false)
              .zipWithIndex
              .map({ case (byteChunk, index) =>
                //if (index % 25 == 0) println(s"index=${index}")
                Frame(camera.mediaInfo.frameSize, byteChunk.toBitVector.toByteArray)
              })
          }
        }
      }))
  }
}

trait CameraAlgebra[F[_]] {

  def readFramesFromCamera(camera: Camera): Stream[F, Frame]

  def makeCamera(devicePath: Path): Stream[F, Camera]

}

case class Camera(devicePath: Path, mediaInfo: MediaInfo)

trait CameraSyntax {

  implicit class CameraOps[F[_]](camera: Camera) {

    def readFrames[F[_] : CameraAlgebra] = F.readFramesFromCamera(camera)

  }

  implicit class PathOps(path: Path){

    def makeCamera[F[_]: CameraAlgebra]: Stream[F, Camera] = F.makeCamera(path)

  }

}

object syntax extends CameraSyntax