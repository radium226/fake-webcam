package radium226

import java.nio.file.{Path, Paths}

import cats.effect.{ExitCode, IO, IOApp}
import fs2._
import radium226.video.splitScenes

package object video {

  case class Size()

  case class Content[F[_]](size: Size, frames: Stream[F, Frame[F]])

  case class Scene[F[_], A](position: Int, video: Video[F, A])

  case class Face()

  type Identity = String

  object Face {

    implicit def defaultInterpolatorForFace[F[_]]: Interpolator[F, Face] = ???

  }

  trait Painter[F[_], A] {

    def paint(a: A, frame: Frame[F[_]]): Frame[F]

  }

  trait Interpolator[F[_], A] {

    def interpolate(): Unit = ???

  }

  trait Tagger[F[_], Value, Tag] {

    def tag(value: Value): F[Tag]

  }

  type Index = Long

  object Tagger {

    def index[F[_], Value](): Tagger[F, Value, Index] = ???

  }

  sealed trait Frame[F[_]]

  sealed abstract class Video[F[_], Value]() {

    // Video
    def analyze[NewValue](f: Video[F, Value] => Video[F, NewValue]): Video[F, NewValue]

    def flatMap[NewValue](f: Value => Video[F, NewValue]): Video[F, NewValue]

    // Value
    def mapValues[NewValue](f: Value => NewValue): Video[F, NewValue]

    def transformValues[NewValue](f: Stream[F, NewValue] => Stream[F, NewValue]): Video[F, NewValue]

    def tapValue(f: Value => F[Unit])


    def map[NewValue](f: Value => NewValue): Video[F, NewValue] = ???


    // Content
    def mapContent(f: Content[F] => Content[F]): Video[F, Value]

    def tapContent(f: Content[F] => F[Unit]): Video[F, Value]

    def analyzeContent[B](f: Content[F] => Stream[F, B]): Video[F, B]


    // Frame
    def analyzeFrames[B](f: Frame[F] => B): Video[F, B]

    def mapFrames(f: Frame[F] => Frame[F]): Video[F, Value]

    def values: Stream[F, Value]

    def content: Content[F]

    // Write
    def writeTo(filePath: Path): Video[F, Unit]



  }

  object Video {

    def readFrom[F[_]](filePath: Path): Video[F, Unit] = ???

  }

  def detectFaces[F[_]](): Frame[F] => List[Face] = ???

  def interpolate[F[_], Value: Interpolator[F, *], Tag](tagger: Tagger[F, Value, Tag]): Pipe[F, List[Value], List[(Tag, Value)]] = ???

  def splitScenes[F[_], Value](): Video[F, Value] => Video[F, Scene[F, Value]] = ???

  def focus[F[_], Value, Tag](): Video[F, List[(Tag, Value)]] => Video[F, (Tag, Video[F, Value])] = ???

  def identifyFaces[F[_]](): Video[F, Face] => Video[F, (Identity, Video[F, Face])] = ???

  object App extends IOApp {


    override def run(args: List[String]): IO[ExitCode] = {
      (for {
        Scene(position, sceneVideo) <- Video.readFrom[IO](Paths.get("video.mp4")).analyze(splitScenes())
        (index, focusedFaceVideo) <- sceneVideo.analyzeFrames(detectFaces()).transformValues(interpolate(Tagger.index[IO, Face]())).analyze(focus[IO, Face, Index]())
        (identity, identifiedFaceVideo) <- focusedFaceVideo.analyze(identifyFaces())
        _ <- identifiedFaceVideo.writeTo(Paths.get(s"s${position}-${identity}-${index}.mp4"))
      } yield ())
        .values
        .compile
        .drain
        .as(ExitCode.Success)
    }

  }

}
