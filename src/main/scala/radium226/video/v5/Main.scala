package radium226.video.v5

import fs2._
import cats._
import cats.effect._
import cats.implicits._
import cats.effect.implicits._

import scala.annotation.tailrec

/*
object Main extends IOApp {

  type Analysis[F[_], A] = Stream[F, Stream[F, A]]

  object Analysis {

    def pure[F[_], A](a: A): Analysis[F, A] = {
      Stream.emit[F, Stream[F, A]](Stream.emit[F, A](a))
    }

  }

  implicit def analysisMonad[F[_]]: Monad[Analysis[F, *]] = new Monad[Analysis[F, *]] {

    override def flatMap[A, B](fa: Analysis[F, A])(f: A => Analysis[F, B]): Analysis[F, B] = {
      fa.flatMap(_.flatMap(f))
    }

    override def tailRecM[A, B](a: A)(f: A => Analysis[F, Either[A, B]]): Analysis[F, B] = {
      f(a).flatMap(_.flatMap({
        case Right(b) =>
          Stream.emit[F, Stream[F, B]](Stream.emit[F, B](b))
        case Left(a) =>
          tailRecM(a)(f)
      }))
    }

    override def pure[A](a: A): Analysis[F, A] = {
      Analysis.pure[F, A](a)
    }

  }

  type Width = Int
  type Height = Int
  type Size = (Width, Height)

  type Frame = String
  type Content[F[_], Feature] = Stream[F, (Frame, Feature)]

  type Video[F[_], Feature] = (Size, Content[F, Feature])
  object Video {
    def sample[F[_]](frames: List[Frame]): Analysis[F, Video[F, Unit]] = {
      Analysis.pure((
        (1, 1),
        Stream
          .emits[F, Frame](frames)
          .map({ frame =>
            frame -> ()
          })))
    }
  }

  override def run(args: List[String]): IO[ExitCode] = {
    (for {
      video <- Video.sample[IO](List("A", "AB", "AB", "B"))
    } yield ())
      .parJoinUnbounded
      .compile
      .drain
      .as(ExitCode.Success)
  }

}*/
