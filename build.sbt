ThisBuild / scalaVersion     := "2.13.3"
ThisBuild / version          := "0.0.1"
ThisBuild / organization     := "radium226"
ThisBuild / organizationName := "Radium226"
ThisBuild / scalacOptions ++= Seq(
  "-deprecation",
  "-feature",
  "-language:_",
  "-unchecked",
  "-Wvalue-discard",
  "-Xfatal-warnings",
  "-Ymacro-annotations"
)

lazy val fs2Dependency = for {
  fs2  <- Dependencies.fs2
  cats <- Dependencies.cats
} yield fs2 exclude(cats.organization, cats.name)

lazy val root = (project in file("."))
  .settings(
    addCompilerPlugin(Dependencies.contextApplied),
    name := "fake-webcam",
    // cats
    libraryDependencies ++= Dependencies.cats,
    // fs2
    libraryDependencies ++= Dependencies.fs2,
    // Scopt
    libraryDependencies ++= Dependencies.scopt,
    // ScalaTest
    libraryDependencies ++= Dependencies.scalaTest map { _ % Test },
    // SLF4J
    libraryDependencies ++= Dependencies.slf4j,

    // GraalVM
    libraryDependencies += "org.scalameta" %% "svm-subs" % "20.2.0",

    // Log4Cats
    libraryDependencies ++= Dependencies.log4cats,

    // Circe
    libraryDependencies ++= Dependencies.circe,

    // Eviction Fix
    dependencyOverrides ++= Dependencies.cats,

    Compile / mainClass := Some("radium226.hello.Hello"),

    assembly / mainClass := Some("radium226.hello.Hello"),
    assembly / assemblyJarName := "fake-webcam.jar",

    graalVMNativeImageCommand := "/usr/lib/jvm/java-11-graalvm/bin/native-image",
    graalVMNativeImageOptions := List(
      "-H:+ReportUnsupportedElementsAtRuntime",
      "--initialize-at-build-time",
      "--no-fallback",
      "--allow-incomplete-classpath",
      "-H:+AddAllCharsets",
      "-H:ResourceConfigurationFiles=../../src/main/graal/resource-config.json",
      "-H:ReflectionConfigurationFiles=../../src/main/graal/reflect-config.json",
      "-H:DynamicProxyConfigurationFiles=../../src/main/graal/proxy-config.json",
      "-H:JNIConfigurationFiles=../../src/main/graal/jni-config.json",
      "-H:Log=registerResource"
    )
  )
  .enablePlugins(GraalVMNativeImagePlugin)