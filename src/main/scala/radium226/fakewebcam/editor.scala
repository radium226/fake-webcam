package radium226.fakewebcam.editor

import java.nio.file.Path

import cats.effect._
import radium226.fakewebcam.camera.{Camera, CameraAlgebra}
import _root_.io.chrisdavenport.log4cats.slf4j.Slf4jLogger
import fs2._
import cats.implicits._
import cats.effect.implicits._
import fs2._
import fs2.concurrent._
import radium226.fakewebcam.camera.syntax._
import radium226.fakewebcam.FakeWebcam2.Action
import radium226.fakewebcam.video._
import radium226.fakewebcam.video.syntax._
import radium226.fakewebcam.input.Input
import radium226.fakewebcam.Frame
import radium226.fakewebcam.mediainfo.MediaInfo

trait EditorAlgebra[F[_]] {


  def edit(defaultFrames: Stream[F, Frame], inputs: Stream[F, Input], mediaInfo: MediaInfo): Stream[F, Frame]

}

case class Editor[F[_]](camera: Camera)



object EditorAlgebra {

  def algebra[F[_]: Sync: Concurrent](videoAlgebra: VideoAlgebra[F]): Resource[F, EditorAlgebra[F]] = {

    val loggerF = Slf4jLogger.fromName[F]("editor")

    Resource
      .liftF[F, EditorAlgebra[F]](loggerF.map({ logger =>
        new EditorAlgebra[F] {

          override def edit(defaultFrames: Stream[F, Frame], inputs: Stream[F, Input], mediaInfo: MediaInfo): Stream[F, Frame] = {
            Stream.eval(Topic[F, Option[Frame]](none[Frame]))
              .flatMap({ defaultFrameTopic =>

                def switchInput: Stream[F, Frame] = {
                  (Stream.emit(Input.Default) ++ inputs)
                    .switchMap({
                      case Input.Default =>
                        Stream.eval(logger.info("Falling back to default")) *> defaultFrameTopic.subscribe(1).drop(1).unNone

                      case Input.File(filePath) =>
                        Stream.eval(logger.info(s"Reading ${filePath} file")) *> (videoAlgebra.readFramesFromVideo(Video(filePath), mediaInfo) ++ defaultFrameTopic.subscribe(1).unNone)
                    })
                }

                switchInput concurrently defaultFrames.map(_.some).through(defaultFrameTopic.publish)

              })
          }
        }
      }))
  }

}
