package radium226.video.v6

import fs2._
import fs2.concurrent._
import cats._
import cats.data.Nested
import cats.effect._
import cats.implicits._
import cats.effect.implicits._

import scala.annotation.tailrec

object utils {

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
            oldValueOptionQueuesByTag
              .toList
              .traverse_({ case (_, valueOptionQueue) =>
                Pull.eval(valueOptionQueue.enqueue1(none[Value]))
              }) >> Pull.done
        })
    }

    go(valuesByTagStream, Map.empty[Tag, Queue[F, Option[Value]]]).stream
  }

}
