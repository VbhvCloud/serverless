package:
	rm -rf package && mkdir package
	pip install --target ./package -r requirements.txt

zip: package
	cd package && zip -r ../my_deployment_package.zip .
	zip my_deployment_package.zip lambda_function.py