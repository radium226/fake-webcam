package radium226
package hello


import cats._
import cats.effect._

import fs2._

import cats.implicits._
import cats.effect.implicits._


object Hello extends IOApp {

    override def run(arguments: List[String]): IO[ExitCode] = {
        Stream
            .emits[IO, String](List("Hello", "World"))
            .compile
            .toList
            .flatMap({ words =>
                IO(println(words.mkString(", ")))
            })
            .as(ExitCode.Success)
    }

}