const form = document.getElementById('encryptForm');
const decryptForm = document.getElementById('decryptForm');
const messageDiv = document.getElementById('message');
const loadingDiv = document.getElementById('loading');

// Encrypt form controls
const modeSelect = document.getElementById('mode');
const ivGroup = document.getElementById('ivGroup');
const nonceGroup = document.getElementById('nonceGroup');

// Decrypt form controls
const decModeSelect = document.getElementById('dec_mode');
const ivGroupDec = document.getElementById('ivGroupDec');
const nonceGroupDec = document.getElementById('nonceGroupDec');

function isHex(str) {
	return /^[0-9a-fA-F]*$/.test(str);
}

function updateFieldsByMode(selectEl, ivEl, nonceEl) {
	const mode = selectEl.value;
	if (['CBC','CFB','OFB'].includes(mode)) {
		ivEl.style.display = 'block';
	} else {
		ivEl.style.display = 'none';
	}
	if (['EAX','CTR'].includes(mode)) {
		nonceEl.style.display = 'block';
	} else {
		nonceEl.style.display = 'none';
	}
}

modeSelect.addEventListener('change', () => updateFieldsByMode(modeSelect, ivGroup, nonceGroup));
decModeSelect.addEventListener('change', () => updateFieldsByMode(decModeSelect, ivGroupDec, nonceGroupDec));
updateFieldsByMode(modeSelect, ivGroup, nonceGroup);
updateFieldsByMode(decModeSelect, ivGroupDec, nonceGroupDec);

form.addEventListener('submit', async (e) => {
	e.preventDefault();
	const file = document.getElementById('file').files[0];
	const key = document.getElementById('key').value;
	const mode = modeSelect.value;
	const iv = document.getElementById('iv').value.trim();
	const nonce = document.getElementById('nonce').value.trim();

	if (!file) { showMessage('请选择文件', 'error'); return; }
	if (![16,24,32].includes(key.length)) { showMessage('密钥长度必须为 16、24 或 32 字节', 'error'); return; }
	if (['CBC','CFB','OFB'].includes(mode)) {
		if (!iv) { showMessage('该模式需要提供 IV（十六进制）', 'error'); return; }
		if (!isHex(iv) || iv.length !== 32) { showMessage('IV 必须为 32 个十六进制字符（16 字节）', 'error'); return; }
	}
	if (nonce && !isHex(nonce)) { showMessage('Nonce 必须为十六进制字符串', 'error'); return; }

	loadingDiv.style.display = 'block'; messageDiv.style.display = 'none';
	try {
		const formData = new FormData();
		formData.append('file', file); formData.append('key', key); formData.append('mode', mode);
		if (iv) formData.append('iv', iv);
		if (nonce) formData.append('nonce', nonce);

		const response = await fetch('/aes/encrypt/', { method: 'POST', body: formData });
		if (response.ok) {
			const data = await response.json(); showMessage(data.message, 'success');
			const encryptedFilename = `encrypted_${file.name}`;
			const downloadResponse = await fetch(`/file/${encryptedFilename}`);
			if (downloadResponse.ok) {
				const blob = await downloadResponse.blob(); const url = window.URL.createObjectURL(blob);
				const a = document.createElement('a'); a.href = url; a.download = encryptedFilename; document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url); document.body.removeChild(a);
			}
			form.reset(); updateFieldsByMode(modeSelect, ivGroup, nonceGroup);
		} else {
			const errorData = await response.json(); showMessage('加密失败: ' + (errorData.detail || '未知错误'), 'error');
		}
	} catch (error) { showMessage('请求失败: ' + error.message, 'error'); }
	finally { loadingDiv.style.display = 'none'; }
});

decryptForm.addEventListener('submit', async (e) => {
	e.preventDefault();
	const file = document.getElementById('dec_file').files[0];
	const key = document.getElementById('dec_key').value;
	const mode = decModeSelect.value;
	const iv = document.getElementById('ivDec').value.trim();
	const nonce = document.getElementById('nonceDec').value.trim();

	if (!file) { showMessage('请选择加密文件', 'error'); return; }
	if (![16,24,32].includes(key.length)) { showMessage('密钥长度必须为 16、24 或 32 字节', 'error'); return; }
	if (['CBC','CFB','OFB'].includes(mode) && iv && (!isHex(iv) || iv.length !== 32)) { showMessage('IV 必须为 32 个十六进制字符（16 字节）', 'error'); return; }
	if (nonce && !isHex(nonce)) { showMessage('Nonce 必须为十六进制字符串', 'error'); return; }

	loadingDiv.style.display = 'block'; messageDiv.style.display = 'none';
	try {
		const formData = new FormData(); formData.append('file', file); formData.append('key', key); formData.append('mode', mode);
		if (iv) formData.append('iv', iv);
		if (nonce) formData.append('nonce', nonce);

		const response = await fetch('/aes/decrypt/', { method: 'POST', body: formData });
		if (response.ok) {
			const data = await response.json(); showMessage(data.message, 'success');
			const decryptedFilename = `decrypted_${file.name}`;
			const downloadResponse = await fetch(`/file/${decryptedFilename}`);
			if (downloadResponse.ok) {
				const blob = await downloadResponse.blob(); const url = window.URL.createObjectURL(blob);
				const a = document.createElement('a'); a.href = url; a.download = decryptedFilename; document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url); document.body.removeChild(a);
			}
			decryptForm.reset(); updateFieldsByMode(decModeSelect, ivGroupDec, nonceGroupDec);
		} else {
			const errorData = await response.json(); showMessage('解密失败: ' + (errorData.detail || '未知错误'), 'error');
		}
	} catch (error) { showMessage('请求失败: ' + error.message, 'error'); }
	finally { loadingDiv.style.display = 'none'; }
});

function showMessage(text, type) { messageDiv.textContent = text; messageDiv.className = `message ${type}`; }
