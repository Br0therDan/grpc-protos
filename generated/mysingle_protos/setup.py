from setuptools import setup

setup(
		name="mysingle_protos",
		version="0.0.0",
		packages=["mysingle_protos", "mysingle_protos.protos"],
		package_dir={
				"mysingle_protos": ".",
				"mysingle_protos.protos": "protos",
		},
		include_package_data=True,
)
