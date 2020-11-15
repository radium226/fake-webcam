SHELL = /bin/bash
.SHELLFLAGS = -o pipefail -e -c
.ONESHELL:

JAVA_HOME = /usr/lib/jvm/java-11-graalvm


.PHONY: clean
clean:
	sbt --java-home "$(JAVA_HOME)" clean

.PHONY: package
package: target/graalvm-native-image/hello target/scala-2.13/hello.jar

target/graalvm-native-image/hello:
	sbt --java-home "$(JAVA_HOME)" "graalvm-native-image:packageBin"

target/scala-2.13/hello.jar:
	sbt --java-home "$(JAVA_HOME)" "assembly"

.PHONY: test
test:
	sbt --java-home "$(JAVA_HOME)" test