package radium226.fakewebcam


import java.nio.file.{Path, Paths}

import cats._
import cats.effect._
import fs2._
import fs2.io.readInputStream
import fs2.text.{lines, utf8Decode}
import cats.implicits._
import cats.effect.implicits._


object input {

  sealed trait Input

  object Input {

    case object Default extends Input

    case class File(filePath: Path) extends Input

  }


  trait InputAlgebra[F[_]] {

    def shell: Stream[F, Input]

  }


  object InputAlgebra {

    def algebra[F[_]: Async: ContextShift](blocker: Blocker): Resource[F, InputAlgebra[F]] = Resource.pure[F, InputAlgebra[F]](new InputAlgebra[F] {

      override def shell: Stream[F, Input] = {
        val filePattern = "^file (.*)$".r("filePath")

        readInputStream[F](F.delay(System.in), 1, blocker)
          .through(utf8Decode[F])
          .through(lines[F])
          .flatMap({
            case "default" =>
              Stream.eval(F.delay(println("> Default"))) *> Stream.emit(Input.Default.some)

            case filePattern(filePath) =>
              Stream.eval(F.delay(println(s"> File(${filePath})"))) *> Stream.emit(Input.File(Paths.get(filePath)).some)

            case "exit" =>
              Stream.eval(F.delay(println(s"> Bye!"))) *> Stream.emit(none[Input])

            case unknown =>
              Stream.eval(F.delay(println(s"> Unknown ${unknown}! "))) *> Stream.empty

          })
          .unNoneTerminate

      }

    })

  }






}


