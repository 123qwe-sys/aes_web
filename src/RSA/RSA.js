function normalizeB64(s) {
    if (!s) return '';
    // backend may return strings like "b'XXXX'" or plain base64
    s = s.toString();
    if (s.startsWith("b'") || s.startsWith('b"')) {
        s = s.slice(2, -1);
    }
    return s;
}

function b64ToUint8Array(b64) {
    return Uint8Array.from(atob(b64), c => c.charCodeAt(0));
}

function downloadBlob(filename, blob) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = filename; document.body.appendChild(a); a.click(); URL.revokeObjectURL(url); a.remove();
}

function showMessage(text, type='success'){
    const el = document.getElementById('message'); el.textContent = text; el.className = 'message ' + (type==='success' ? 'success' : 'error'); el.style.display = 'block';
}

function setLoading(on){ document.getElementById('loading').style.display = on ? 'block' : 'none'; }

document.getElementById('genKeys').addEventListener('click', async () => {
    const size = parseInt(document.getElementById('key_size').value || '2048');
    setLoading(true); showMessage('', 'success');
    try {
        const fd = new FormData(); fd.append('key_size', size);
        const resp = await fetch('/rsa/generate_keys/', { method: 'POST', body: fd });
        if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail || '生成失败'); }
        const data = await resp.json();
        const pub = normalizeB64(data.public_key_file);
        const priv = normalizeB64(data.private_key_file);
        document.getElementById('publicKey').value = pub;
        document.getElementById('privateKey').value = priv;
        document.getElementById('enc_pub').value = pub;
        document.getElementById('dec_priv').value = priv;
        showMessage(data.message || '密钥生成成功', 'success');
    } catch (e) { showMessage('生成失败: ' + e.message, 'error'); }
    finally { setLoading(false); }
});

document.getElementById('downloadPub').addEventListener('click', () => {
    const val = normalizeB64(document.getElementById('publicKey').value);
    if (!val) { showMessage('无可下载的公钥', 'error'); return; }
    const blob = new Blob([val], {type:'text/plain'});
    downloadBlob('public_key.b64', blob);
});

document.getElementById('downloadPriv').addEventListener('click', () => {
    const val = normalizeB64(document.getElementById('privateKey').value);
    if (!val) { showMessage('无可下载的私钥', 'error'); return; }
    const blob = new Blob([val], {type:'text/plain'});
    downloadBlob('private_key.b64', blob);
});

document.getElementById('encryptBtn').addEventListener('click', async () => {
    const fileEl = document.getElementById('enc_file'); const file = fileEl.files && fileEl.files[0];
    const pub = normalizeB64(document.getElementById('enc_pub').value);
    if (!file) { showMessage('请选择文件', 'error'); return; }
    if (!pub) { showMessage('请提供公钥（Base64）', 'error'); return; }
    setLoading(true); try {
        const fd = new FormData(); fd.append('file', file);
        const pubFileInput = document.getElementById('enc_pub_file');
        if (pubFileInput.files && pubFileInput.files[0]) {
            fd.append('public_key', pubFileInput.files[0]);
        } else {
            fd.append('public_key', new Blob([pub], {type:'text/plain'}), 'public_key.b64');
        }
        const resp = await fetch('/rsa/encrypt/', { method: 'POST', body: fd });
        if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail || '加密失败'); }
        const data = await resp.json(); showMessage(data.message || '加密成功', 'success');
        const encryptedName = `encrypted_${file.name}`;
        const down = await fetch(`/file/${encryptedName}`);
        if (down.ok) { const blob = await down.blob(); downloadBlob(encryptedName, blob); }
    } catch(e){ showMessage('加密失败: ' + e.message, 'error'); }
    finally { setLoading(false); }
});

document.getElementById('decryptBtn').addEventListener('click', async () => {
    const fileEl = document.getElementById('dec_file'); const file = fileEl.files && fileEl.files[0];
    const priv = normalizeB64(document.getElementById('dec_priv').value);
    if (!file) { showMessage('请选择文件', 'error'); return; }
    if (!priv) { showMessage('请提供私钥（Base64）', 'error'); return; }
    setLoading(true); try {
        const fd = new FormData(); fd.append('file', file);
        const privFileInput = document.getElementById('dec_priv_file');
        if (privFileInput.files && privFileInput.files[0]) {
            fd.append('private_key', privFileInput.files[0]);
        } else {
            fd.append('private_key', new Blob([priv], {type:'text/plain'}), 'private_key.b64');
        }
        const resp = await fetch('/rsa/decrypt/', { method: 'POST', body: fd });
        if (!resp.ok) { const err = await resp.json(); throw new Error(err.detail || '解密失败'); }
        const data = await resp.json(); showMessage(data.message || '解密成功', 'success');
        const decryptedName = `decrypted_${file.name}`;
        const down = await fetch(`/file/${decryptedName}`);
        if (down.ok) { const blob = await down.blob(); downloadBlob(decryptedName, blob); }
    } catch(e){ showMessage('解密失败: ' + e.message, 'error'); }
    finally { setLoading(false); }
});
