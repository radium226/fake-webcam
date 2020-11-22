package radium226.fakewebcam.mediainfo

import java.nio.file.Path

import cats._
import io.chrisdavenport.log4cats.slf4j.Slf4jLogger
import cats.effect.{Blocker, Concurrent, ContextShift, Resource, Sync}
import io.circe.parser.decode
import io.circe.Decoder
import io.circe.HCursor
import fs2._
import fs2.io._
import fs2.text._
import cats.implicits._
import cats.effect.implicits._

case class Size(width: Long, height: Long)

case class MediaInfo(frameSize: Size, pixelFormat: PixelFormat, framePerSecond: FramePerSecond)

sealed trait PixelFormat

object FramePerSecond {

  implicit val defaultDecoder = Decoder[String].emap({ framePerSecondAsString =>
    parse(framePerSecondAsString).toRight(s"Unable to parse ${framePerSecondAsString} as FramePerSecond")
  })

  val Regex = "([0-9]+)/([0-9]+)".r("images", "seconds")

  def parse(frameRateAsString: String): Option[FramePerSecond] = for {
    groups <- Regex.findFirstMatchIn(frameRateAsString)
    images <- groups.group("images").toIntOption
    seconds <- groups.group("seconds").toIntOption
  } yield FramePerSecond(images / seconds)

}

case class FramePerSecond(value: Int)

object PixelFormat {

  implicit val defaultDecoder: Decoder[PixelFormat] = Decoder[String].emap({ pixelFormatAsString =>
    parse(pixelFormatAsString).toRight(s"Unable to parse ${pixelFormatAsString} as PixelFormat")
  })

  case object YUYV422 extends PixelFormat

  def parse(text: String): Option[PixelFormat] = text match {
    case "yuyv422" =>
      YUYV422.some

    case _ =>
      none[PixelFormat]
  }

  def format(pixelFormat: PixelFormat): String = pixelFormat match {
    case YUYV422 =>
      "yuyv422"
  }

}

object MediaInfo {

  implicit val defaultDecoder: Decoder[MediaInfo] = { hcursor =>
    for {
      width <- hcursor.downField("streams").downArray.downField("width").as[Long]
      height <- hcursor.downField("streams").downArray.downField("height").as[Long]
      size = Size(width, height)
      pixelFormat <- hcursor.downField("streams").downArray.downField("pix_fmt").as[PixelFormat]
      framePerSecond <- hcursor.downField("streams").downArray.downField("r_frame_rate").as[FramePerSecond]
    } yield MediaInfo(size, pixelFormat, FramePerSecond(24))
  }

}

trait MediaInfoAlgebra[F[_]] {

  def probeMediaInfo(devicePath: Path): Stream[F, MediaInfo]

}

object FFmpegMediaInfoAlgebra {

  def algebra[F[_]: Sync: ContextShift: Concurrent](blocker: Blocker): Resource[F, MediaInfoAlgebra[F]] = {
    Resource.liftF(Slf4jLogger.fromName[F]("ffmpegMediaInfo")).map({ logger =>
      new MediaInfoAlgebra[F] {

        val ChunkSize = 512

        override def probeMediaInfo(devicePath: Path): Stream[F, MediaInfo] = {
          val ffprobeCommand = List("ffprobe",
            "-loglevel", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            s"${devicePath}",
          )

          val ffprobeProcessBuilder = new ProcessBuilder()
            .redirectInput(ProcessBuilder.Redirect.INHERIT)
            .redirectError(ProcessBuilder.Redirect.PIPE)
            .redirectOutput(ProcessBuilder.Redirect.PIPE)
            .command(ffprobeCommand: _*)

          val ffprobeOutputStream = Stream
            .eval[F, Process](F.delay(ffprobeProcessBuilder.start()))
            .flatMap({ ffprobeProcess =>
              val errorStream = readInputStream(F.delay(ffprobeProcess.getErrorStream), ChunkSize, blocker)
                .through(utf8Decode[F])
                .through(lines[F])
                .evalMap({ line => logger.debug(line) })
                .drain

              val outputStream = readInputStream[F](F.delay(ffprobeProcess.getInputStream), ChunkSize, blocker)

              outputStream concurrently errorStream
            })


          def foldOption[A]: Pipe[F, Option[A], A] = {
            _.flatMap(_.fold[Stream[F, A]](Stream.raiseError[F](new NoSuchElementException()))({ a => Stream.emit[F, A](a) }))
          }

          def foldEither[L, R]: Pipe[F, Either[L, R], R] = {
            _.flatMap(_.fold({ l => Stream.raiseError[F](new IllegalArgumentException(s"${l}")) }, { r => Stream.emit[F, R](r) }))
          }

          ffprobeOutputStream
            .through(utf8Decode[F])
            .foldMonoid
            .last
            .through(foldOption)
            .map(decode[MediaInfo])
            .through(foldEither)
        }
      }
    })
  }

}

trait MediaInfoSyntax {

  implicit class PathOps(path: Path) {

    def probeMediaInfo[F[_]: MediaInfoAlgebra]: Stream[F, MediaInfo] = F.probeMediaInfo(path)

  }

}

object syntax extends MediaInfoSyntax
