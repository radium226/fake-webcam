package radium226.fakewebcam


import java.nio.file.Paths

import fs2._
import cats.effect._
import radium226.fakewebcam.camera.{Camera, CameraAlgebra, CameraSyntax}
import radium226.fakewebcam.mediainfo.{FFmpegMediaInfoAlgebra, MediaInfoAlgebra}
import cats.implicits._
import cats.effect.implicits._
import radium226.fakewebcam.fakecamera.{FakeCamera, FakeCameraAlgebra, V4L2LoopbackFakeCameraAlgebra}

case class Algebras[F[_]](
   mediaInfo: MediaInfoAlgebra[F],
   camera: CameraAlgebra[F],
   fakeCamera: FakeCameraAlgebra[F]
 )

object Main extends IOApp {

  import mediainfo.syntax._
  import camera.syntax._
  import fakecamera.syntax._

  implicit def mediaInfoAlgebraForAlgebras[F[_]](implicit algebras: Algebras[F]): MediaInfoAlgebra[F] = algebras.mediaInfo
  implicit def cameraAlgebraForAlgebras[F[_]](implicit algebras: Algebras[F]): CameraAlgebra[F] = algebras.camera
  implicit def fakeCameraAlgebraForAlgebras[F[_]](implicit algebras: Algebras[F]): FakeCameraAlgebra[F] = algebras.fakeCamera

  override def run(arguments: List[String]): IO[ExitCode] = {
    val algebrasResource = for {
      cameraBlocker <- Blocker[IO]
      fakeCameraBlocker <- Blocker[IO]
      mediaInfoAlgebra <- FFmpegMediaInfoAlgebra.algebra[IO](cameraBlocker)
      cameraAlgebra <- CameraAlgebra.algebra[IO](cameraBlocker, mediaInfoAlgebra)
      fakeCameraAlgebra <- V4L2LoopbackFakeCameraAlgebra.algebra[IO](fakeCameraBlocker)
    } yield Algebras(mediaInfoAlgebra, cameraAlgebra, fakeCameraAlgebra)

    algebrasResource
      .use({ implicit algebras =>
        /* algebras.camera.makeCamera(Paths
          .get("/dev/video0"))
          .flatMap({ camera =>
            Stream
              .resource(algebras.fakeCamera.fakeCameraResource("Fake Camera"))
              .flatMap({ fakeCamera =>
                camera
                  .readFrames[IO]
                  .through(fakeCamera.writeFrames[IO](camera.mediaInfo))
              })
          })
          .compile
          .drain
          .as(ExitCode.Success) */
        algebras.fakeCamera.fakeCameraResource(("Fake Camera"))
          .use({ _ => IO.never })
          .as(ExitCode.Success)
      })
  }

}
