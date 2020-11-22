package radium226
package fakewebcam

import java.nio.file.Paths

import cats.effect.{Blocker, IO, Resource}

class ProbeSpec extends AbstractSpec {

  "Probe" should "be able to probe /dev/video0" in {
    /*Blocker[IO]
      .flatMap({ blocker =>
        Resource.liftF(ProbeAlgebra.dsl[IO](blocker))
      })
      .use({ probeAlgebra =>
        probeAlgebra.probe(Paths.get("/dev/video0")).compile.last
      })
      .flatMap(_.fold(fail())({ probe =>
        IO(println(probe))
      }))
      .unsafeRunSync()*/
  }


}