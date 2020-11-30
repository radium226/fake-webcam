package radium226.fakewebcam.main

import java.nio.file.Paths

import cats.effect.{Blocker, ExitCode, IO, IOApp}
import fs2.Stream
import radium226.fakewebcam.Algebras
import radium226.fakewebcam.camera.CameraAlgebra
import radium226.fakewebcam.fakecamera.V4L2LoopbackFakeCameraAlgebra
import radium226.fakewebcam.mediainfo.FFmpegMediaInfoAlgebra
import radium226.fakewebcam.camera.syntax._
import radium226.fakewebcam.editor.EditorAlgebra
import radium226.fakewebcam.fakecamera.syntax._
import radium226.fakewebcam.input
import radium226.fakewebcam.input.InputAlgebra
import radium226.fakewebcam.video.VideoAlgebra

object FakeWebcam extends IOApp {

  override def run(args: List[String]): IO[ExitCode] = {
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
        implicit val cameraAlgebra = algebras.camera
        implicit val fakeCameraAlgebra = algebras.fakeCamera
        implicit val editorAlgebra = algebras.editor

        (for {
          camera <- algebras.camera.makeCamera(Paths.get("/dev/video2"))
          _ = println(camera.mediaInfo)
          fakeCamera <- Stream.resource(algebras.fakeCamera.fakeCameraResource("Fake Camera"))
        } yield (camera, fakeCamera))
          .flatMap({ case (camera, fakeCamera) =>
            algebras
              .editor
              .edit(camera.readFrames[IO], algebras.input.shell, camera.mediaInfo)
              .through(fakeCamera.writeFrames[IO](camera.mediaInfo))
          })
          .compile
          .drain
          .as(ExitCode.Success)
      })


  }

}
