package radium226.fakewebcam


import java.nio.file.Paths

import fs2._
import cats.effect._
import radium226.fakewebcam.camera.{Camera, CameraAlgebra, CameraSyntax}
import radium226.fakewebcam.mediainfo.{FFmpegMediaInfoAlgebra, MediaInfoAlgebra}
import cats.implicits._
import cats.effect.implicits._
import fs2.concurrent.{Queue, Topic}
import radium226.fakewebcam.editor.EditorAlgebra
import radium226.fakewebcam.fakecamera.{FakeCamera, FakeCameraAlgebra, V4L2LoopbackFakeCameraAlgebra}
import radium226.fakewebcam.input.InputAlgebra
import radium226.fakewebcam.video.VideoAlgebra

case class Algebras[F[_]](
   mediaInfo: MediaInfoAlgebra[F],
   camera: CameraAlgebra[F],
   fakeCamera: FakeCameraAlgebra[F],
   editor: EditorAlgebra[F],
   input: InputAlgebra[F]
 )

object Main extends IOApp {

  import mediainfo.syntax._
  import camera.syntax._
  import fakecamera.syntax._

  sealed trait Input

  case object Input {

    case class Video(filePath: Paths) extends Input

    case object Camera extends Input

  }

  implicit def mediaInfoAlgebraForAlgebras[F[_]](implicit algebras: Algebras[F]): MediaInfoAlgebra[F] = algebras.mediaInfo
  implicit def cameraAlgebraForAlgebras[F[_]](implicit algebras: Algebras[F]): CameraAlgebra[F] = algebras.camera
  implicit def fakeCameraAlgebraForAlgebras[F[_]](implicit algebras: Algebras[F]): FakeCameraAlgebra[F] = algebras.fakeCamera

  override def run(arguments: List[String]): IO[ExitCode] = {
    val algebrasResource = for {
      cameraBlocker <- Blocker[IO]
      fakeCameraBlocker <- Blocker[IO]
      inputBlocker <- Blocker[IO]
      videoBlocker <- Blocker[IO]
      mediaInfoAlgebra <- FFmpegMediaInfoAlgebra.algebra[IO](cameraBlocker)
      cameraAlgebra <- CameraAlgebra.algebra[IO](cameraBlocker, mediaInfoAlgebra)
      fakeCameraAlgebra <- V4L2LoopbackFakeCameraAlgebra.algebra[IO](fakeCameraBlocker)
      videoAlgebra <- VideoAlgebra.algebra[IO](videoBlocker)
      editorAlgebra <- EditorAlgebra.algebra[IO](videoAlgebra)
      inputAlgebra <- InputAlgebra.algebra[IO](inputBlocker)
    } yield Algebras(mediaInfoAlgebra, cameraAlgebra, fakeCameraAlgebra, editorAlgebra, inputAlgebra)

    algebrasResource
      .use({ implicit algebras =>
        algebras.camera.makeCamera(Paths
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
          .as(ExitCode.Success)
        /*algebras.fakeCamera.fakeCameraResource(("Fake Camera"))
          .use({ _ => IO.never })
          .as(ExitCode.Success)*/
      })
  }

}
