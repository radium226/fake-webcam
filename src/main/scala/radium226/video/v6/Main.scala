package radium226.video.v6

import fs2._
import fs2.concurrent._
import cats._
import cats.data.Nested
import cats.effect._
import cats.implicits._
import cats.effect.implicits._

import scala.annotation.tailrec


object Main extends IOApp {

  import analysis.Tracking

  type Width = Int
  type Height = Int
  case class Size(width: Width, height: Height)

  type Frame = String
  type Content[F[_], Value] = Stream[F, (Frame, Value)]
  case class Video[F[_], Value](size: Size, content: Content[F, Value])


  trait Lens[Feature] {

    def focus(feature: Feature, frame: Frame): Frame

  }


  class Analysis[F[_], A](val value: Stream[F, Stream[F, A]])

  trait AnalysisInstances {

    implicit def analysisMonad[F[_]]: Monad[Analysis[F, *]] = new Monad[Analysis[F, *]] {

      override def flatMap[A, B](fa: Analysis[F, A])(f: A => Analysis[F, B]): Analysis[F, B] = {
        new Analysis[F, B](fa.value.flatMap({ streamOfA =>
          streamOfA.flatMap({ a =>
            f(a).value
          })
        }))
      }

      override def tailRecM[A, B](a: A)(f: A => Analysis[F, Either[A, B]]): Analysis[F, B] = {
        new Analysis[F, B](f(a).value.flatMap(_.flatMap({
          case Left(a) =>
            tailRecM(a)(f).value

          case Right(b) =>
            Stream(Stream(b))
        })))
      }

      override def pure[A](x: A): Analysis[F, A] = {
        Analysis(x)
      }
    }
  }

  object Analysis extends AnalysisInstances {

    def apply[F[_], Value](value: Value): Analysis[F, Value] = {
      new Analysis[F, Value](Stream(Stream(value)))
    }

    def apply[F[_], Value](value: Stream[F, Stream[F, Value]]): Analysis[F, Value] = {
      new Analysis[F, Value](value)
    }

  }

  type Position = Long
  case class Scene[F[_], Feature](position: Position, video: Video[F, Feature])

  trait AnalysisSyntax {

    implicit class AnalysisOps[F[_], Value](analysis: Analysis[F, Value]) {

      def stream(implicit F: Concurrent[F]): Stream[F, Value] = {
        analysis
          .value
          .parJoinUnbounded
      }

    }

  }

  object analysisSyntax extends AnalysisSyntax

  trait SceneSplitter[F[_]] {

    def shouldSplitScene(oldFrame: Frame, newFrame: Frame): F[Boolean]

  }

  trait VideoAlgebra[F[_]] {

    def focus[Feature](video: Video[F, Feature])(implicit lensForFeature: Lens[Feature]): Video[F, Feature] = {
      video
        .copy(content = video
          .content
          .map({ case (frame, feature) =>
            lensForFeature.focus(feature, frame) -> feature
          }))
    }

    def splitScenes[Feature](video: Video[F, Feature])(sceneSplitter: SceneSplitter[F]): Analysis[F, Scene[F, Feature]]

    def drain[Feature](video: Video[F, Feature]): Analysis[F, Unit]

    def play[Value](video: Video[F, Value])(label: Label): Video[F, Value]

    def repeat[Feature](video: Video[F, Feature]): Video[F, Feature] = {
      video.copy(content = video.content.repeat)
    }

    type VideoAnalysis[F[_], A, B] = Video[F, A] => Analysis[F, B]

    def analyze[A, B](video: Video[F, A])(videoAnalysis: VideoAnalysis[F, A, B]): Analysis[F, B] = {
      videoAnalysis(video)
    }

    def tagFeatures[FeatureInstance, Tag](video: Video[F, List[FeatureInstance]])(tagger: Tagger[F, FeatureInstance, Tag]): Video[F, Map[Tag, FeatureInstance]] = {
      mapFeature(video)(tagger.tag)
    }

    def featuresThrough[Feature, NewFeature](video: Video[F, Feature])(pipe: Pipe[F, Feature, NewFeature]): Video[F, NewFeature] = {
      video.copy(content = video.content.flatMap({ case (frame, feature) =>
        pipe(Stream(feature)).map({ newFeature => (frame -> newFeature)})
      }))
    }

    def mapFeature[Feature, NewFeature](video: Video[F, Feature])(f: Feature => NewFeature): Video[F, NewFeature] = {
      video.copy(content = video.content.map({ case (frame, feature) =>
        frame -> f(feature)
      }))
    }

    def extractFeatures[FeatureInstance](video: Video[F, _])(extractor: Extractor[F, FeatureInstance]): Video[F, List[FeatureInstance]] = {
      video.copy(content = video.content.map({ case (frame, feature) =>
        frame -> extractor.extract(frame)
      }))
    }

  }

  trait Tagger[F[_], FeatureInstance, Tag] {

    def tag(featureInstances: List[FeatureInstance]): Map[Tag, FeatureInstance]

  }

  trait Extractor[F[_], FeatureInstance] {

    def extract(frame: Frame): List[FeatureInstance]

  }

  trait VideoSyntax {

    implicit class VideoOps[F[_], Feature](video: Video[F, Feature])(implicit F: VideoAlgebra[F], concurrent: Concurrent[F]) {

      def splitScenes(sceneSplitter: SceneSplitter[F]): Analysis[F, Scene[F, Feature]] = {
        F.splitScenes(video)(sceneSplitter)
      }

      def drain: Analysis[F, Unit] = {
        F.drain(video)
      }

      def play(label: Label): Video[F, Feature] = F.play(video)(label)

      def focus(implicit focusForFeature: Lens[Feature]): Video[F, Feature] = F.focus(video)

      def repeat: Video[F, Feature] = F.repeat(video)

      def featuresThrough[NewFeature](pipe: Pipe[F, Feature, NewFeature]): Video[F, NewFeature] = {
        video.copy(content = video.content.flatMap({ case (frame, feature) =>
          pipe(Stream(feature)).map({ newFeature => (frame -> newFeature)})
        }))
      }

      def mapFeature[NewFeature](f: Feature => NewFeature): Video[F, NewFeature] = {
        video.copy(content = video.content.map({ case (frame, feature) =>
          frame -> f(feature)
        }))
      }

      def tagFeatures[FeatureInstance, Tag](tagger: Tagger[F, FeatureInstance, Tag])(implicit evidence: Feature =:= List[FeatureInstance]): Video[F, Map[Tag, FeatureInstance]] = {
        F.tagFeatures[FeatureInstance, Tag](video.asInstanceOf[Video[F, List[FeatureInstance]]])(tagger)
      }

      def extractFeatures[FeatureInstance](extractor: Extractor[F, FeatureInstance]): Video[F, List[FeatureInstance]] = {
        F.extractFeatures(video)(extractor)
      }

      def track[FeatureInstance, Tag](implicit evidence: Map[Tag, FeatureInstance] =:= Feature): Analysis[F, Tracking[F, FeatureInstance, Tag]] = {
        analysis.Track.track(video.asInstanceOf[Video[F, Map[Tag, FeatureInstance]]])
      }

    }

  }

  object videoSyntax extends VideoSyntax

  type Label = String

  trait VideoInstances {

    implicit def defaultVideoAlgebra[F[_]](implicit F: Concurrent[F]): VideoAlgebra[F] = new VideoAlgebra[F] {

      def drain[Feature](video: Video[F, Feature]): Analysis[F, Unit] = {
        Analysis(Stream(video.content.drain))
      }

      def play[Value](video: Video[F, Value])(label: Label): Video[F, Value] = {
        video.copy(content = video.content.evalTap({ case (frame, feature) => F.delay(println(s" -[ ${label} ]-> frame=${frame} / feature=${feature}")) }))
      }

      def splitScenes[Feature](video: Video[F, Feature])(sceneSplitter: SceneSplitter[F]): Analysis[F, Scene[F, Feature]] = {
        type QueueOfContent = Queue[F, Option[(Frame, Feature)]]
        type QueueOfQueueOfContent = Queue[F, Option[QueueOfContent]]
        type FF = (Frame, Feature)

        def go(content: Stream[F, (Option[FF], FF)], currentQueueOfContentOption: Option[QueueOfContent], queueOfQueueOfContent: QueueOfQueueOfContent):  Pull[F, Unit, Unit] = {
          content.pull.uncons1.flatMap({
            case Some(((Some((oldFrame, oldFeature)), (newFrame, newFeature)), remainingContent)) =>
              currentQueueOfContentOption match {
                case Some(currentQueueOfContent) =>
                  for {
                    split <- Pull.eval(sceneSplitter.shouldSplitScene(oldFrame, newFrame))
                    _ <- if (split) for {
                      _ <- Pull.eval(currentQueueOfContent.enqueue1(none))
                      newCurrentQueueOfContent <- Pull.eval(Queue.bounded[F, Option[(Frame, Feature)]](1))
                      _ <- Pull.eval(queueOfQueueOfContent.enqueue1(newCurrentQueueOfContent.some))
                      _ <- Pull.eval(newCurrentQueueOfContent.enqueue1((newFrame -> newFeature).some))
                      _ <- go(remainingContent, newCurrentQueueOfContent.some, queueOfQueueOfContent)
                    } yield () else for {
                      _ <- Pull.eval(currentQueueOfContent.enqueue1((newFrame -> newFeature).some))
                      _ <- go(remainingContent, currentQueueOfContent.some, queueOfQueueOfContent)
                    } yield ()
                  } yield ()

                case None =>
                  for {
                    currentQueueOfContent <- Pull.eval(Queue.bounded[F, Option[(Frame, Feature)]](1))
                    _ <- Pull.eval(queueOfQueueOfContent.enqueue1(currentQueueOfContent.some))
                    _ <- go(Stream(((oldFrame -> oldFeature).some, (newFrame -> newFeature))) ++ remainingContent, currentQueueOfContent.some, queueOfQueueOfContent)
                  } yield ()
              }

            case Some(((None, (newFrame, newFeature)), remainingContent)) =>
              currentQueueOfContentOption match {
                case Some(currentQueueOfContent) =>
                  for {
                    _ <- Pull.eval(currentQueueOfContent.enqueue1((newFrame -> newFeature).some))
                    _ <- go(remainingContent, currentQueueOfContent.some, queueOfQueueOfContent)
                  } yield ()

                case None =>
                  for {
                    currentQueueOfContent <- Pull.eval(Queue.unbounded[F, Option[(Frame, Feature)]])
                    _ <- Pull.eval(queueOfQueueOfContent.enqueue1(currentQueueOfContent.some))
                    _ <- go(Stream((none, (newFrame -> newFeature))) ++ remainingContent, currentQueueOfContent.some, queueOfQueueOfContent)
                  } yield ()
              }

            case None =>
              currentQueueOfContentOption match {
                case Some(currentQueueOfContent) =>
                  for {
                    _ <- Pull.eval(currentQueueOfContent.enqueue1(none[(Frame, Feature)]))
                    _ <- Pull.eval(queueOfQueueOfContent.enqueue1(none[QueueOfContent]))
                    _ <- Pull.done
                  } yield ()

                case None =>
                  for {
                    _ <- Pull.eval(queueOfQueueOfContent.enqueue1(none[QueueOfContent]))
                    _ <- Pull.done
                  } yield ()
              }

          })

        }

        val streamOfStream: Stream[F, Stream[F, Scene[F, Feature]]] = Stream
          .eval(Queue.unbounded[F, Option[Queue[F, Option[(Frame, Feature)]]]])
          .map({ queueOfQueueOfContent =>
            val scenes: Stream[F, Scene[F, Feature]] = queueOfQueueOfContent
              .dequeue
              .unNoneTerminate
              .zipWithIndex
              .map({ case (queueOfContent, position) =>
                Scene(position, Video(video.size, queueOfContent.dequeue.unNoneTerminate))
              })

            val drain = go(video.content.zipWithPrevious, none[QueueOfContent], queueOfQueueOfContent).stream

            scenes.concurrently(drain)
          });

        Analysis[F, Scene[F, Feature]](
          streamOfStream
        )
      }

    }

  }

  object videoInstances extends VideoInstances

  object Video {

    def sample[F[_]](frames: List[Frame]): Analysis[F, Video[F, Unit]] = {
      Analysis(
        Video(
          Size(1, 1),
          Stream
            .emits[F, Frame](frames)
            .map({ frame =>
              frame -> ()
            }))
      )
    }

  }

  import analysisSyntax._

  import videoInstances._
  import videoSyntax._

  implicit val lensForLetter: Lens[String] = new Lens[String] {

    override def focus(feature: String, frame: Frame): Frame = {
      feature
    }

  }

  override def run(args: List[String]): IO[ExitCode] = {

    (for {
      fullVideo <- Video.sample[IO](List("A", "AB", "AB", "B", "CA", "CA"))
      scene <- fullVideo.repeat.splitScenes(new SceneSplitter[IO] {

        override def shouldSplitScene(oldFrame: Frame, newFrame: Frame): IO[Boolean] = {
          IO.pure(!newFrame.toList.exists({ char => oldFrame.contains(char) }))
        }

      })

      tracking <- scene
        .video
        .extractFeatures[String](_.toList.map(_.toString))
        .tagFeatures[String, String](new Tagger[IO, String, String] {

          override def tag(featureInstances: List[String]): Map[String, String] = {
            featureInstances.groupBy({ letter => letter }).view.mapValues(_.head).toMap
          }

        })
        .track[String, String]
      _ <- tracking
        .video
        .focus
        .play(s"scene-${scene.position}-${tracking.tag}")
        .drain
    } yield ())
      .stream
      .compile
      .drain
      .as(ExitCode.Success)
  }

}
