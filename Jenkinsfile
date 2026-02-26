podTemplate(
    //idleMinutes : 30,
    podRetention : onFailure(),
    activeDeadlineSeconds : 7200,
    containers: [
        containerTemplate(
            name: 'dtk-rpm-builder', 
            image: 'docker-production.packages.idmod.org/idm/dtk-rpm-builder:0.1',
            command: 'sleep', 
            args: '30d'
            )
  ]) {
  node(POD_LABEL) {
    container('dtk-rpm-builder'){
			def build_ok = true
			stage('Cleanup Workspace') {		    
				cleanWs()
				echo "Cleaned Up Workspace For Project"
			}
			stage('Prepare') {
				sh 'python3 -m pip install --upgrade pip'
				sh "pip3 install wheel"
				//workarround for https://github.com/InstituteforDiseaseModeling/idmtools/issues/1893
				sh "pip3 install pygit2==1.10.1"  
				sh 'python3 -m pip install --upgrade setuptools'
				sh 'pip3 freeze'
				//sh 'yum -y remove mpich'
				//sh 'yum -y install mpich-3.2'
				//sh 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/lib64/mpich/lib'
			}
			stage('Code Checkout') {
				if (env.CHANGE_ID) {
					echo "I execute on the pull request ${env.CHANGE_ID}"
					checkout([$class: 'GitSCM',
					branches: [[name: "pr/${env.CHANGE_ID}/head"]],
					doGenerateSubmoduleConfigurations: false,
					extensions: [],
					gitTool: 'Default',
					submoduleCfg: [],
					userRemoteConfigs: [[refspec: '+refs/pull/*:refs/remotes/origin/pr/*', credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2', url: 'git@github.com:InstituteforDiseaseModeling/emodpy-malaria.git']]])
				} else {
					echo "I execute on the ${env.BRANCH_NAME} branch"
					git branch: "${env.BRANCH_NAME}",
					credentialsId: '704061ca-54ca-4aec-b5ce-ddc7e9eab0f2',
					url: 'git@github.com:InstituteforDiseaseModeling/emodpy-malaria.git'
				}
			}
			stage('Build') {
				sh 'pwd'
				sh 'ls -a'
				sh 'python3 setup.py bdist_wheel'
				 
			}
			stage('Install') {
				def curDate = sh(returnStdout: true, script: "date").trim()
				echo "The current date is ${curDate}"
				
				echo "I am installing emodpy-malaria from wheel file built from code"
				def wheelFile = sh(returnStdout: true, script: "find ./dist -name '*.whl'").toString().trim()
				//def wheelFile = sh(returnStdout: true, script: "python3 ./.github/scripts/get_wheel_filename.py --package-file setup.py").toString().trim()
				echo "This is the package file: ${wheelFile}"
				sh "pip3 install $wheelFile --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple"
				 
				//sh "pip3 install dataclasses"
				sh 'pip3 install keyrings.alt'
				sh "pip3 freeze"
			}
			stage('Login') {
				withCredentials([usernamePassword(credentialsId: 'comps_jenkins_user', usernameVariable: 'COMPS_USERNAME', passwordVariable: 'COMPS_PASSWORD'),
					         usernamePassword(credentialsId: 'comps2_jenkins_user', usernameVariable: 'COMPS2_USERNAME', passwordVariable: 'COMPS2_PASSWORD')]) {
					dir('tests') {
					    sh 'python3 create_auth_token_args.py --comps_url https://comps2.idmod.org --username $COMPS2_USERNAME --password $COMPS2_PASSWORD'
					    sh 'python3 create_auth_token_args.py --comps_url https://comps.idmod.org --username $COMPS_USERNAME --password $COMPS_PASSWORD'
					}
			    	}
			}

			try{
				stage('ReadMe Test') {
					echo "Running ReadMe Tests"
					dir('tests/doc_tests') {
						sh 'pip3 install pytest'
						sh 'python3 run_tests.py'
						junit '**/*test*.xml'
					}
				}
			} catch(e) {
				build_ok = false
				echo e.toString()  
			}

			try{
				stage('Run Tests and Get Coverage') {		    
					echo "Running examples"
					dir('tests/unittests') {
						sh 'pip3 install coverage xmlrunner'
						sh 'python3 get_unittest_coverage.py'
						archiveArtifacts artifacts: 'coverage.tar.gz', allowEmptyArchive: false
						junit 'test_reports/*.xml'
					}
				}
			} catch(e) {
				build_ok = false
				echo e.toString()  
			}

			stage('Run Examples') {		    
			echo "Running examples"
				dir('examples') {
					sh 'pip3 install snakemake'
					// pulp workaround for https://github.com/snakemake/snakemake/issues/2607
                    sh 'pip3 install pulp==2.7.0'
					sh 'snakemake --cores=10 --config python_version=python3'
				}
			}

			if(build_ok) {
				currentBuild.result = "SUCCESS"
			} else {
				currentBuild.result = "FAILURE"
			}
		}
	}
  }




