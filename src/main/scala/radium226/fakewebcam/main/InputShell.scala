package radium226.fakewebcam.main

import cats.effect.{Blocker, ExitCode, IO, IOApp, Resource}
import radium226.fakewebcam.input
import fs2._
import cats._
import cats.implicits._
import cats.effect.implicits._
import radium226.fakewebcam.input.InputAlgebra

object InputShell extends IOApp {

  override def run(args: List[String]): IO[ExitCode] = {
    val resources: Resource[IO, (Blocker, InputAlgebra[IO])] = for {
      blocker <- Blocker[IO]
      inputAlgebra <- InputAlgebra.algebra[IO](blocker)
    } yield (blocker, inputAlgebra)

    resources
      .use({ case (blocker, inputAlgebra) =>
        inputAlgebra
          .shell
          .evalMap({ input =>
            IO(println(s" --> input=${input}"))
          })
          .compile
          .drain
          .as(ExitCode.Success)
      })


  }

}
