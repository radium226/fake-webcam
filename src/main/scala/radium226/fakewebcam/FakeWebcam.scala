package radium226.fakewebcam
import cats._
import cats.effect._
import fs2._
import cats.implicits._
import cats.effect.implicits._
import fs2.concurrent.{Queue, Topic}

import scala.concurrent.duration._


object FakeWebcam extends IOApp {

  sealed trait Action

  object Action {

    case object Webcam extends Action

    case object Loop extends Action

  }

  type Frame = String

  override def run(args: List[String]): IO[ExitCode] = {
    val actionStream = Stream.emit[IO, Action](Action.Webcam) ++ Stream.emits[IO, Action](List(Action.Webcam, Action.Loop, Action.Webcam, Action.Loop, Action.Webcam)).metered(5 second)
    (for {
      webcamTopic <- Stream.eval(Topic[IO, Frame]("initial-frame"))
      actionQueue <- Stream.eval(Queue.bounded[IO, Action](1))
      outputQueue <- Stream.eval(Queue.bounded[IO, Frame](1))
    } yield (webcamTopic, actionQueue, outputQueue))
      .flatMap({ case (webcamTopic, actionQueue, outputQueue) =>

        val webcamStream = Stream.fromIterator[IO](Iterator.from(0)).map({ index => s"webcam-${index}"}).metered(0.04 seconds).through(webcamTopic.publish)
        val controlStream = control(webcamTopic, actionQueue, outputQueue)

        outputQueue.dequeue concurrently controlStream concurrently webcamStream concurrently actionStream.through(actionQueue.enqueue)
      })
      .evalMap({ outputFrame => IO(println(s" -[output]-> ${outputFrame}")) })
      .compile
      .drain
      .as(ExitCode.Success)
  }

  def control(webcamTopic: Topic[IO, Frame], actionQueue: Queue[IO, Action], outputQueue: Queue[IO, Frame]): Stream[IO, Unit] = {
    actionQueue
      .dequeue
      .switchMap({
        case Action.Webcam =>
          webcamTopic.subscribe(1).drop(1)

        case Action.Loop =>
          Stream.emits[IO, Frame](List("loop-1", "loop-2", "loop-3")).metered(0.04 seconds).onFinalize(IO(println("Closing loop"))) ++ webcamTopic.subscribe(1)
      })
      .through(outputQueue.enqueue)
  }

}