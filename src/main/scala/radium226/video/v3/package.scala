package radium226.video.v3

import fs2._
import fs2.concurrent.Queue
import cats._
import cats.effect._
import cats.implicits._
import cats.effect.implicits._

/*object Main extends IOApp {

  implicit class MapOps[Key, OneValue](oneMap: Map[Key, OneValue]) {

    def fullOuterJoin[OtherValue](otherMap: Map[Key, OtherValue]): Map[Key, (Option[OneValue], Option[OtherValue])] = {
      (oneMap ++ otherMap)
        .keys
        .toList
        .distinct
        .map({ key =>
          key -> (oneMap.get(key), otherMap.get(key))
        })
        .toMap
    }

  }



  def streamValuesByTag[F[_], Tag, Value]()(implicit F: Concurrent[F]): Pipe[F, Map[Tag, Value], (Tag, Stream[F, Value])] = { valuesByTagStream =>

    def go(valuesByTagStream: Stream[F, Map[Tag, Value]], oldValueOptionQueuesByTag: Map[Tag, Queue[F, Option[Value]]]): Pull[F, (Tag, Stream[F, Value]), Unit] = {
      valuesByTagStream
        .pull
        .uncons1
        .flatMap({
          case Some((valuesByTag, remainingValuesByTagStream)) =>
            //println(s"fullOuterJoin=${valuesByTag fullOuterJoin oldValueOptionQueuesByTag} / valuesByTag=${valuesByTag}")
            for {
              newValueOptionQueuesByTag <-  (valuesByTag fullOuterJoin oldValueOptionQueuesByTag)
                .toList
                //.map({ a => println(s"a=${a}") ;  a })
                .foldLeftM(Map.empty[Tag, Queue[F, Option[Value]]])({
                  case (newValueOptionQueuesByTag, (tag, (Some(value), Some(valueOptionQueue)))) =>
                    Pull.eval(valueOptionQueue.enqueue1(value.some)) >> Pull.pure(newValueOptionQueuesByTag + (tag -> valueOptionQueue))

                  case (newValueOptionQueuesByTag, (tag, (Some(value), None))) =>
                    for {
                      valueOptionQueue <- Pull.eval(Queue.unbounded[F, Option[Value]])
                      _                <- Pull.output1((tag -> valueOptionQueue.dequeue.unNoneTerminate))
                      _                <- Pull.eval(valueOptionQueue.enqueue1(value.some))
                    } yield newValueOptionQueuesByTag + (tag -> valueOptionQueue)

                  case (newValueOptionQueuesByTag, (_, (None, Some(valueOptionQueue)))) =>
                    Pull.eval(valueOptionQueue.enqueue1(none[Value])) >> Pull.pure(newValueOptionQueuesByTag)

                  case (newValueOptionQueuesByTag, (_, (None, None))) =>
                    Pull.pure(newValueOptionQueuesByTag)
                })
              _ <- go(remainingValuesByTagStream, newValueOptionQueuesByTag)
            } yield ()

          case None =>
            println("None! ")
            oldValueOptionQueuesByTag
              .toList
              .traverse_({ case (_, valueOptionQueue) =>
                Pull.eval(valueOptionQueue.enqueue1(none[Value]))
              }) >> Pull.done
        })
    }

    go(valuesByTagStream, Map.empty[Tag, Queue[F, Option[Value]]]).stream
  }

  type Frame = String

  type Mark = String

  case class Tracking[F[_], Tag, Value](tag: Tag, video: Video[F, Value])

  sealed abstract class Operation[F[_], +Value] {

    def flatMap[NewValue](f: Value => Operation[F, NewValue]): Operation[F, NewValue] = Operation.Bind(this, f)

  }

  case class FrameAndValue[Value](frame: Frame, value: Value)

  object Operation {

    case class Pure[F, Value](value: Value) extends Operation[F, Value]

    case class Play[F[_], Value](operation: Operation[F, Value], mark: Mark) extends Operation[F, Value]

    case class Track[F[_], Tag, Value](operation: Operation[F, Map[Tag, Value]]) extends Operation[F, Tracking[F, Tag, Value]]

    case class Read[F[_]](frames: List[Frame]) extends Operation[F, Unit]

    case class Scenes[F[_], Value](operation: Operation[F, Value]) extends Operation[F, Scene[F, Value]]

    case class Bind[F, Value, NewValue](operation: Operation[F, Value], f: Value => Operation[F, NewValue]) extends Operation[F, NewValue]


  }

  def materialize[F[_], Value](operation: Operation[F, Value])(implicit F: Concurrent[F]): Stream[F, Value] = {
    operation match {
      case Operation.Play(operation, mark) =>
        materialize(operation)
          .evalTap({ case FrameAndValue(frame, value) =>
            F.delay(println(s"-[ ${mark} ]-> ${value}"))
          })

      case Operation.Bind(operation, f) =>
        materialize(operation)
          .flatMap({ value =>
            materialize[F, Any](f(value))
          })

      case Operation.Read(frames) =>
        Stream
          .emits(frames)
          .map({ frame =>
            FrameAndValue(frame, ())
          })
          .asInstanceOf[Stream[F, FrameAndValue[Value]]]

      case Operation.Track(operation) =>
        materialize[F, Map[Any, Any]](operation)
          .through(streamValuesByTag[F, Any, Any]())



    }

  }

  implicit class VideoOfMapOfTagAndValue[F[_], Tag, Value](video: Video[F, Map[Tag, Value]]) {

    def track: Video[F, Tracking[F, Tag, Value]] = new Video[F, Tracking[F, Tag, Value]](Operation.Track(video.operation))

  }

  type Position = Int

  case class Scene[F, Value](position: Position, video: Video[F, Value])


  class Video[F[_], Value](private[v3] val operation: Operation[F, Value]) {

    def flatMap[NewValue](f: Value => Video[F, NewValue]): Video[F, NewValue] = new Video[F, NewValue](operation.flatMap(f(_).operation))

    def map[NewValue](f: Value => NewValue): Video[F, NewValue] = ???

    def play(mark: Mark): Video[F, Value] = new Video(Operation.Play(operation, mark))

    def scenes: Video[F, Scene[F, Value]] = new Video(Operation.Scenes(operation))

    def run(implicit F: Concurrent[F]): Stream[F, Unit] = {
      materialize[F, Any](operation).void
    }

  }

  object Video {

    def pure[F[_], Value](value: Value): Video[F, Value] = new Video[F, Value](Operation.Pure(value))

    def frames[F[_]](frames: Frame*): Video[F, Unit] = new Video[F, Unit](Operation.Read(frames.toList))

  }


  override def run(arguments: List[String]): IO[ExitCode] = {
    (for {
      scene <- Video.frames[IO]("A", "AB", "AB", "B").scenes
      _     <- scene.video.play(mark = s"${scene.position}")
    } yield ())
      .run
      .compile
      .drain
      .as(ExitCode.Success)


    /*val video = Stream.emits[IO, Frame](List("A", "AB", "AB", "B", "A"))


    video
      .map(_.toList.map(_.toString))
      .map({ letters =>
        letters.groupBy({ letter => letter }).view.mapValues(_.head).toMap
      })
      .through(streamValuesByTag())
      .map({ case (tag, letterStream) =>
        letterStream
        .evalMap({ letter =>
          IO(println(s"${tag} -> ${letter}"))
        })
      })
      .parJoinUnbounded
      .compile
      .drain
      .as(ExitCode.Success)*/

  }

}*/
