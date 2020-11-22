package radium226

import cats.effect._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

import scala.concurrent.ExecutionContext


abstract class AbstractSpec extends AnyFlatSpec with Matchers {

  implicit val executionContext: ExecutionContext = ExecutionContext.global

  implicit val contextShiftForIO: ContextShift[IO] = IO.contextShift(executionContext)

  implicit val timerForIO: Timer[IO] = IO.timer(executionContext)

}