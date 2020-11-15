import sbt._

object Dependencies {

  lazy val scalaTest = Seq(
    "org.scalatest" %% "scalatest" % "3.2.3"
  )

  lazy val cats = Seq(
    "org.typelevel" %% "cats-core" % "2.2.0",
    "org.typelevel" %% "cats-effect" % "2.2.0",
    "org.typelevel" %% "kittens" % "2.2.0",
    "org.typelevel" %% "mouse" % "0.25"
  )

  lazy val fs2 = Seq(
    "co.fs2" %% "fs2-core" % "2.4.5",
    "co.fs2" %% "fs2-io" % "2.4.5"
  )

  lazy val fs2Process = Seq(
    "eu.monniot" %% "fs2-process" % "0.3.0"
  )

  lazy val chronicleQueue = Seq(
    "net.openhft" % "chronicle-queue" % "5.20.4"
  )

  lazy val contextApplied = "org.augustjune" %% "context-applied" % "0.1.4"

  lazy val circe = Seq("circe-core", "circe-parser", "circe-generic").map({ name => "io.circe" %% name % "0.13.0" })

  lazy val shapeless = Seq(
    "com.chuusai" %% "shapeless" % "2.3.3"
  )

  lazy val nuProcess = Seq(
    "com.zaxxer" % "nuprocess" % "2.0.1"
  )

  lazy val selenium = Seq(
    "org.seleniumhq.selenium" % "selenium-java" % "3.141.59"
  )

  lazy val http4s = Seq("http4s-core", "http4s-blaze-server", "http4s-dsl").map({ name => "org.http4s" %% name % "0.21.7" })

  lazy val scopt = Seq("com.github.scopt" %% "scopt" % "4.0.0-RC2")

  lazy val logback = Seq("ch.qos.logback" % "logback-classic" % "1.2.3")

  lazy val slf4j = Seq("org.slf4j" % "slf4j-simple" % "1.7.30")

}
