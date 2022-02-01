package radium226.video

import fs2._
import fs2.io.file._
import java.nio.file.{Path, Paths}

import cats.effect.{Blocker, Concurrent, ContextShift, Sync}

package object v2 {

  /*type Frame = String


  type Width = Int

  type Height = Int

  type Size

  def probeSize[F[_]](byteStream: Stream[F, Byte]): Stream[F, (Size, Stream[F, Byte])] = ???

  def readFrames[F[_]](size: Size, byteStream: Stream[F, Byte]): Stream[F, Frame] = ???

  def readBytes[F[_]](filePath: Path): Stream[F, Byte] = ???

  def splitScenes[F[_]](frameStream: Stream[F, Frame]): Stream[F, Stream[F, Frame]] = ???


  sealed trait Source[F[_], Value]

  object Source {

    case class File[F[_]](filePath: Path) extends Source[F, Unit]

    case class Frames[F[_], Value](size: Size, stream: Stream[F, (Frame, Value)]) extends Source[F, Value]

    case class Play[F[_], Value](source: Source[F, Value], player: Player) extends Source[F, Value]

  }

  def drainSource[F[_], Value](source: Source[F, Value])(implicit F: Concurrent[F], contextShift: ContextShift[F]): Stream[F, Unit] = {
    source match {
      case Source.File(filePath) =>
        probeSize(Stream
          .resource[F, Blocker](Blocker[F])
          .flatMap({ blocker =>
            readAll(filePath, blocker, 1024)
          }))
          .flatMap({ case (size, byteStream) =>
            drainSource[F, Unit](Source.Frames(size, readFrames(size, byteStream)
              .map({ frame =>
                (frame, ())
              })))
          })

      case Source.Play(Source.Frames(size, frameStream), Player.MPlayer) =>
        frameStream
          .evalTap({ case (frame, _) =>
            F.delay(println(frame))
          })
          .drain
    }
  }

  sealed trait Player

  object Player {

    case object MPlayer extends Player

  }

  final class Video[F[_]: Concurrent: ContextShift, Value](source: Source[F, Value]) {

    def play(player: Player): Video[F, Value] = new Video[F, Value](Source.Play(source, player))

    def drain: Stream[F, Unit] = drainSource(source)

  }

  object Video {

    def file[F[_]](filePath: Path): Video[F, Unit] = {
      new Video(Source.File(filePath))
    }

  }*/

}
