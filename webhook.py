from flask import Flask, request, jsonify  # 导入 Flask 框架、请求处理和 JSON 响应模块
import json
import ssl
import base64

app = Flask(__name__)  # 创建一个 Flask 应用实例


def create_patch(metadata):
	"""
	创建 JSON Patch 以添加 'mutate' 注释。
	如果 metadata.annotations 不存在，则首先创建该路径。
	"""
	if 'labels' in metadata:
		dic = metadata['labels']
	else:
		dic = {}

	patch = [
		# 添加 'labels' 键，如果不存在
		{'op': 'add', 'path': '/metadata/labels', 'value': dic},
		# 添加 'environment' 标签
		{'op': 'add', 'path': '/metadata/labels/environment', 'value': 'production'}
	]

	patch_json = json.dumps(patch)
	patch_base64 = base64.b64encode(patch_json.encode('utf-8')).decode('utf-8')
	return patch_base64


@app.route('/mutate', methods=['POST'])  # https://webhook-service.default.svc:443/mutate
def mutate():
	"""
	处理 Mutating Webhook 的请求，对 Pod 对象应用 JSON Patch。
	"""
	admission_review = request.get_json()  # 从请求中提取 AdmissionReview 对象

	# 验证 AdmissionReview 格式是否正确
	# admission_review['request']['object']
	if 'request' not in admission_review or 'object' not in admission_review['request']:
		return jsonify({
			'kind': 'AdmissionReview',
			'apiVersion': 'admission.k8s.io/v1',
			'response': {
				'allowed': False,  # 如果格式无效，则禁止当前提交过来的资源请求
				'status': {'message': 'Invalid AdmissionReview format'}
			}
		})

	req = admission_review['request']  # 提取请求对象
	print('--->',req)
	# 生成 JSON Patch
	metata = req['object']['metadata']
	patch_json = create_patch(metata)

	# 准备 AdmissionResponse 响应
	admission_response = {
		'kind': 'AdmissionReview',
		'apiVersion': 'admission.k8s.io/v1',
		'response': {
			'uid': req['uid'],
			'allowed': True,
			'patchType': 'JSONPatch',
			'patch': patch_json  # 直接包含 Patch 数据作为 JSON 字符串
		}
	}

	print(admission_response)
	return jsonify(admission_response)
	
@app.route('/fujg', methods=['GET',])  # https://webhook-service.default.svc:443/mutate
def fujg_test():
	"测试代码 没啥用"
	return "hello world from fujg"

if __name__ == '__main__':
	# 加载 SSL 证书和私钥
	context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
	context.load_cert_chain('/certs/tls.crt', '/certs/tls.key')

	# Run the Flask application with SSL
	app.run(host='0.0.0.0', port=443, ssl_context=context)
