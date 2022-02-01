package radium226.video.v6.analysis

import fs2._
import fs2.concurrent._
import cats._
import cats.data.Nested
import cats.effect._
import cats.implicits._
import cats.effect.implicits._
import radium226.video.v6.Main.{Analysis, Content, Frame, Video}

case class Tracking[F[_], Shape, Tag](tag: Tag, video: Video[F, Shape])

object Track {

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

  def track[F[_], Feature, Tag](video: Video[F, Map[Tag, Feature]])(implicit F: Concurrent[F]): Analysis[F, Tracking[F, Feature, Tag]] = {
    def go(content: Content[F, Map[Tag, Feature]], queuesByTag: Map[Tag, Queue[F, Option[(Frame, Feature)]]], queueOfQueue: Queue[F, Option[(Tag, Queue[F, Option[(Frame, Feature)]])]]): Pull[F, Nothing, Unit] = {
      content
        .pull
        .uncons1
        .flatMap({
          case Some(((frame, featuresByTag), remainingContent)) =>
            for {
              newQueuesByTag <- (featuresByTag fullOuterJoin queuesByTag)
                .toList
                .foldLeftM(Map.empty[Tag, Queue[F, Option[(Frame, Feature)]]])({
                  case (newQueuesByTag, (tag, (Some(feature), Some(queue)))) =>
                    for {
                      _ <- Pull.eval(queue.enqueue1((frame -> feature).some))
                    } yield newQueuesByTag + (tag -> queue)

                  case (newQueuesByTag, (tag, (Some(feature), None))) =>
                    for {
                      queue <- Pull.eval(Queue.unbounded[F, Option[(Frame, Feature)]])
                      _ <- Pull.eval(queue.enqueue1((frame -> feature).some))
                      _ <- Pull.eval(queueOfQueue.enqueue1((tag -> queue).some))
                    } yield newQueuesByTag + (tag -> queue)

                  case (newQueuesByTag, (_, (None, Some(queue)))) =>
                    for {
                      _ <- Pull.eval(queue.enqueue1(none[(Frame, Feature)]))
                    } yield newQueuesByTag

                  case (newQueuesByTag, (_, (None, None))) =>
                    Pull.pure[F, Map[Tag, Queue[F, Option[(Frame, Feature)]]]](newQueuesByTag)
                })
              _ <- go(remainingContent, newQueuesByTag, queueOfQueue)
            } yield ()

          case None =>
            for {
              _ <- queuesByTag
                .toList
                .traverse_({ case (_, queue) =>
                  Pull.eval(queue.enqueue1(none))
                })
              _ <- Pull.eval(queueOfQueue.enqueue1(none))
              _ <- Pull.done
            } yield ()
        })
    }

    Analysis(
      Stream
        .eval(Queue.unbounded[F, Option[(Tag, Queue[F, Option[(Frame, Feature)]])]])
        .map({ queueOfQueue =>
          queueOfQueue
            .dequeue
            .unNoneTerminate
            .map({ case (tag, trackingVideoContentQueue) =>
              val trackingVideo = Video[F, Feature](video.size, trackingVideoContentQueue.dequeue.unNoneTerminate)
              Tracking(tag, trackingVideo)
            })
            .concurrently(go(video.content, Map.empty[Tag, Queue[F, Option[(Frame, Feature)]]], queueOfQueue).stream)
        })
    )
  }

}
