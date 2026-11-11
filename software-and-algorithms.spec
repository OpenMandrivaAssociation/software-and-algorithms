Name:		software-and-algorithms
Version:	1.0
Release:	1
Summary:	Java implementations of classic algorithms
Group:		Development/Java
License:	MIT
URL:		https://github.com/KevinStern/software-and-algorithms
# No release tag. Commit d428bbbe matches the Maven Central 1.0 sources.
%global commit d428bbbe0451dd168c59d1f874a7a73f6b93719b
Source0:	https://github.com/KevinStern/software-and-algorithms/archive/%{commit}.tar.gz#/software-and-algorithms-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem

%description
com.github.kevinstern:software-and-algorithms %{version} includes the
Hungarian assignment algorithm Error Prone 2.50.0 calls from
TermEditDistance.

%prep
%autosetup -n software-and-algorithms-%{commit}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
find src/main/java -name '*.java' > sources.list
test "$(wc -l < sources.list)" -eq 10
mkdir -p classes
javac --release 8 -encoding UTF-8 -d classes @sources.list
cat > manifest.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: blogspot.software.and.algorithms

EOF
jar cfm software-and-algorithms.jar manifest.mf -C classes .
jar i software-and-algorithms.jar
javap -verbose -cp software-and-algorithms.jar blogspot.software_and_algorithms.stern_library.optimization.HungarianAlgorithm | grep -F 'major version: 52'
jar --describe-module --file software-and-algorithms.jar > describe.txt
if grep -F -q 'Unable to derive' describe.txt; then
	cat describe.txt
	exit 1
fi
jar tf software-and-algorithms.jar | grep -E 'module-info|\.(java|jar|so|node|wasm)$' && exit 1 || true

cat > software-and-algorithms.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>com.github.kevinstern</groupId>
  <artifactId>software-and-algorithms</artifactId>
  <version>1.0</version>
  <name>Software and Algorithms</name>
  <description>Java implementations of classic algorithms</description>
  <url>https://github.com/KevinStern/software-and-algorithms</url>
  <licenses>
    <license>
      <name>MIT License</name>
      <url>https://opensource.org/licenses/MIT</url>
    </license>
  </licenses>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact software-and-algorithms.pom:software-and-algorithms.jar \
	--file-name software-and-algorithms \
	--filelist .mfiles

%check
set -eo pipefail
JAR=%{buildroot}%{_javadir}/software-and-algorithms.jar
test -f "$JAR"
mkdir -p check
cat > check/Smoke.java << 'EOF'
import blogspot.software_and_algorithms.stern_library.optimization.HungarianAlgorithm;
public class Smoke {
	public static void main(String[] args) {
		double[][] cost = {
			{4, 1, 3},
			{2, 0, 5},
			{3, 2, 2}
		};
		int[] assignment = new HungarianAlgorithm(cost).execute();
		double total = 0;
		StringBuilder sb = new StringBuilder();
		for (int i = 0; i < assignment.length; i++) {
			if (i > 0) {
				sb.append(',');
			}
			sb.append(assignment[i]);
			if (assignment[i] >= 0) {
				total += cost[i][assignment[i]];
			}
		}
		System.out.println("saa_ok " + sb + " " + total);
	}
}
EOF
javac --release 8 -encoding UTF-8 -cp "$JAR" -d check check/Smoke.java
java -cp "check:$JAR" Smoke > check/check.log
cat check/check.log
grep -F -q 'saa_ok 1,0,2 5.0' check/check.log

%files -f .mfiles
%license LICENSE
