package radium226.video.v4

import java.nio.file.Path

import fs2._
import fs2.concurrent._

import cats._
import cats.effect._

import cats.implicits._
import cats.effect.implicits._

/*
object Main extends IOApp {

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
              newValueOptionQueuesByTag <- (valuesByTag fullOuterJoin oldValueOptionQueuesByTag)
                .toList
                //.map({ a => println(s"a=${a}") ;  a })
                .foldLeftM(Map.empty[Tag, Queue[F, Option[Value]]])({
                  case (newValueOptionQueuesByTag, (tag, (Some(value), Some(valueOptionQueue)))) =>
                    Pull.eval(valueOptionQueue.enqueue1(value.some)) >> Pull.pure(newValueOptionQueuesByTag + (tag -> valueOptionQueue))

                  case (newValueOptionQueuesByTag, (tag, (Some(value), None))) =>
                    for {
                      valueOptionQueue <- Pull.eval(Queue.unbounded[F, Option[Value]])
                      _ <- Pull.output1((tag -> valueOptionQueue.dequeue.unNoneTerminate))
                      _ <- Pull.eval(valueOptionQueue.enqueue1(value.some))
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
  type Content[F[_], Value] = Stream[F, (Frame, Value)]

  type Width = Int
  type Height = Int

  case class Size(width: Width, height: Height)

  sealed abstract class Stage[F[_], A] {
    self =>

    def flatMap[B](f: A => Stage[F, B]): Stage[F, B] = Stage.FlatMap(self, f)

    def map[B](f: A => B): Stage[F, B] = self.flatMap({ a => Stage.Pure[F, B](f(a)) })

  }

  object Stage {

    case class Play[F[_], Feature](video: Video[F, Feature], label: Label) extends Stage[F, Unit]

    case class SplitScenes[F[_], Value](video: Video[F, Value]) extends Stage[F, Scene[F, Value]]

    case class TrackTag[F[_], Tag, Value](video: Video[F, Map[Tag, Value]]) extends Stage[F, Tracking[F, Tag, Value]]

    case class FlatMap[F, Value, NewValue](s: Stage[F, Value], f: Value => Stage[F, NewValue]) extends Stage[F, NewValue]

    case class Pure[F, A](a: A) extends Stage[F, A]

  }

  type Label = String

  class Video[F[_], Feature](val size: Size, val content: Content[F, Feature])

  type Position = Int

  case class Scene[F, Value](position: Position, video: Video[F, Value])

  case class Tracking[F, Tag, Value](tag: Tag, video: Video[F, Value])

  trait FeatureExtractor[F[_], Feature] {

    def extractFeature(frame: Frame): Feature

  }

  trait FeaturesTagger[F[_], Feature, Tag] {

    def tagFeatures(features: List[Feature]): Map[Tag, Feature]

  }

  object Video {

    def extractFeature[F[_], Feature](video: Video[F, _])(featureExtractor: FeatureExtractor[F, Feature]): Video[F, Feature] = {
      new Video(
        video.size,
        video
          .content
          .map({ case (frame, _) =>
            frame -> featureExtractor.extractFeature(frame)
          })
      )
    }

    def mapFeature[F[_], Feature, NewFeature](video: Video[F, Feature])(f: Feature => NewFeature): Video[F, NewFeature] = {
      new Video(
        video.size,
        video
          .content
          .map({ case (frame, feature) =>
            frame -> f(feature)
          })
      )
    }

    def tag[F[_], Feature, Tag](video: Video[F, List[Feature]])(featuresTagger: FeaturesTagger[F, Feature, Tag]): Video[F, Map[Tag, Feature]] = {
      mapFeature(video)(featuresTagger.tagFeatures)
    }

    def play[F[_], Feature](video: Video[F, Feature])(label: Label)(implicit F: Sync[F]): Stage[F, Unit] = Stage.Play[F, Feature](video, label)

    def splitScenes[F[_], Value](video: Video[F, Value]): Stage[F, Scene[F, Value]] = Stage.SplitScenes(video)

    def trackTag[F[_], Tag, Value](video: Video[F, Map[Tag, Value]]): Stage[F, Tracking[F, Tag, Value]] = Stage.TrackTag(video)

    def sample[F[_]](frames: Frame*): Stage[F, Video[F, Unit]] = {
      Video(
        Size(1, 1),
        Stream
          .emits[F, Frame](frames)
          .map({ frame =>
            frame -> ()
          }))
    }

    def apply[F[_], Value](size: Size, content: Content[F, Value]): Stage[F, Video[F, Value]] = Stage.Pure(new Video(size, content))

  }

  object videoSyntax {

    implicit class VideoWithAnyFeatureOps[F[_], Feature](video: Video[F, Feature]) {

      def splitScenes: Stage[F, Scene[F, Feature]] = Video.splitScenes(video)

      def extractFeature[NewFeature](featureExtractor: FeatureExtractor[F, NewFeature]): Video[F, NewFeature] = Video.extractFeature[F, NewFeature](video)(featureExtractor)

      def play(label: Label)(implicit F: Sync[F]): Stage[F, Unit] = Video.play(video)(label)

    }

    implicit class VideoWithMapOfTagAndFeatureAsFeatureOps[F[_], Tag, Feature](video: Video[F, Map[Tag, Feature]]) {

      def trackTag: Stage[F, Tracking[F, Tag, Feature]] = Video.trackTag(video)

    }

  }

  def splitScenes[F[_], Feature](content: Content[F, Feature]): Stream[F, Content[F, Feature]] = ???

  def evaluate[F[_], Feature](stage: Stage[F, Feature])(implicit F: Concurrent[F]): Stream[F, Feature] = {
    stage match {
      case Stage.Play(video, label) =>
        video
          .content
          .asInstanceOf[Content[F, Any]]
          .evalMap({ case (frame, _) =>
            F.delay(println(s"[play/${label}] ${frame}"))
          })
          .asInstanceOf[Stream[F, Feature]]

      case Stage.FlatMap(s, f) =>
        evaluate(s)
          .flatMap({ feature =>
            evaluate(f(feature))
          })

      case Stage.SplitScenes(video) =>
        splitScenes(video.content)



    }
  }

  import videoSyntax._

  override def run(arguments: List[String]): IO[ExitCode] = {
    val stage: Stage[IO, Unit] = for {
      sampleVideo <- Video.sample[IO]("A", "AB", "AB", "B", "A")
      scene <- sampleVideo.splitScenes
      _ <- scene.video.play(s"scene.position=${scene.position}")
    } yield ()

    evaluate(stage).compile.drain.as(ExitCode.Success)
  }

}
*/