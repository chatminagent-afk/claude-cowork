# -*- coding: utf-8 -*-
"""
Assembler workflow n8n VIRA-PCR (rerunnable).
Load node-params V4/TEMPLATE dari _extraction, modifikasi, gabung, dump 3 JSON + validasi.
"""
import json, os, re, uuid, sys

BASE = os.path.dirname(os.path.abspath(__file__))              # .../_extraction/build
EXTRACT = os.path.dirname(BASE)                                # .../_extraction
V4P = os.path.join(EXTRACT, 'V4', 'V4-node-params')
TPLP = os.path.join(EXTRACT, 'TEMPLATE', 'TEMPLATE-node-params')
DRAFT_DIR = os.path.dirname(os.path.dirname(EXTRACT))          # .../Persada Cisoka Residence
OUT_DIR = os.path.dirname(EXTRACT)                             # .../draft workflow

sys.path.insert(0, BASE)
import codenodes as C

# ---- Placeholders (semua secret -> placeholder / credential) ----
GCRED = {"id": "REPLACE_WITH_PCR_GOOGLE_CRED_ID", "name": "Google Service Account PCR (REPLACE)"}
KCRED = {"id": "REPLACE_WITH_KIRIMI_CUSTOM_AUTH_CRED_ID", "name": "Kirimi Custom Auth (REPLACE per client)"}
ACRED = {"id": "REPLACE_WITH_PCR_ANTHROPIC_CRED_ID", "name": "Anthropic account PCR (REPLACE)"}
SHEET_ID_EXPR = "={{ $('Bootstrap Config').first().json.sheet_id }}"

def load(folder, name):
    with open(os.path.join(folder, name + '.json'), 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def newid():
    return str(uuid.uuid4())

def scrub(node):
    """Buang jejak The Scholars / sheet id / cred id produksi dari string node."""
    s = json.dumps(node, ensure_ascii=False)
    reps = {
        "1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE": "PLACEHOLDER_SHEET_ID",
        "3gTKMbD8lJDLbRqR": GCRED["id"],
        "DPNnlN1bTbbMf8ks": ACRED["id"],
        "The_Scholars_Database": "PCR_Database",
        "thescholars": "pcr",
        "The Scholars": "PCR",
        "TheScholars": "PCR",
        "Scholars": "PCR",
        "scholars": "pcr",
        "SAMA SAM": "SAMA TIM",
        "[VIRA]": "[PCR]",
    }
    for a, b in reps.items():
        s = s.replace(a, b)
    # kata "Sam" berdiri sendiri -> "Admin"
    s = re.sub(r'\bSam\b', 'Admin', s)
    return json.loads(s)

def gen_schema(value_keys):
    schema = []
    for k in value_keys:
        entry = {"id": k, "displayName": k, "required": False, "defaultMatch": False,
                 "display": True, "type": "string", "canBeUsedToMatch": True}
        if k == "row_number":
            entry["type"] = "number"; entry["readOnly"] = True
        schema.append(entry)
    return schema

def patch_sheets(node, sheet_name, columns_value=None, matching=None, operation=None):
    p = node["parameters"]
    p["documentId"] = {"__rl": True, "value": SHEET_ID_EXPR, "mode": "id"}
    p["sheetName"] = {"__rl": True, "value": sheet_name, "mode": "name"}
    if operation is not None:
        p["operation"] = operation
    node["credentials"] = {"googleApi": dict(GCRED)}
    if "columns" in p:
        if columns_value is not None:
            p["columns"]["value"] = columns_value
            p["columns"]["matchingColumns"] = matching if matching is not None else []
        # regen schema dari value keys (buang kolom legacy dari JSON)
        vals = list(p["columns"]["value"].keys())
        p["columns"]["schema"] = gen_schema(vals)
    return node

def set_ids(node):
    node["id"] = newid()
    return node

# ================= NODE BUILDERS =================
NODES = []
POS = {"x": -1600, "y": 0}
def place():
    POS["x"] += 220
    return [POS["x"], POS["y"]]

def code_node(name, jscode, per_item=False, extra=None):
    params = {"jsCode": jscode}
    if per_item:
        params["mode"] = "runOnceForEachItem"
    n = {"parameters": params, "type": "n8n-nodes-base.code", "typeVersion": 2,
         "position": place(), "id": newid(), "name": name}
    if extra:
        n.update(extra)
    return n

def if_bool(name, expr):
    return {"parameters": {"conditions": {"options": {"caseSensitive": True, "typeValidation": "loose", "version": 2},
            "conditions": [{"id": newid(), "leftValue": expr, "rightValue": "",
            "operator": {"type": "boolean", "operation": "true", "singleValue": True}}], "combinator": "and"},
            "looseTypeValidation": True, "options": {}},
            "type": "n8n-nodes-base.if", "typeVersion": 2.2, "position": place(), "id": newid(), "name": name}

def kirimi_from_template(tpl_name, new_name, message_expr=None, phone_expr=None, extra_params=None, err_out=True):
    # Ambil dari TEMPLATE (sudah pola httpCustomAuth). Fallback V4 + konversi.
    tpl_path = os.path.join(TPLP, tpl_name + '.json')
    if os.path.exists(tpl_path):
        n = scrub(load(TPLP, tpl_name))
    else:
        n = scrub(load(V4P, tpl_name))
        # konversi plaintext -> httpCustomAuth
        params = n["parameters"]
        plist = params.get("bodyParameters", {}).get("parameters", [])
        params["bodyParameters"]["parameters"] = [it for it in plist if it["name"] not in ("user_code", "secret", "device_id")]
        params["authentication"] = "genericCredentialType"
        params["genericAuthType"] = "httpCustomAuth"
    n["name"] = new_name
    set_ids(n)
    n["credentials"] = {"httpCustomAuth": dict(KCRED)}
    params = n["parameters"]
    plist = params["bodyParameters"]["parameters"]
    def setp(k, v):
        for item in plist:
            if item["name"] == k:
                item["value"] = v; return
        plist.append({"name": k, "value": v})
    if phone_expr is not None:
        setp("phone", phone_expr)
    if message_expr is not None:
        setp("message", message_expr)
    if extra_params:
        for k, v in extra_params.items():
            setp(k, v)
    n["position"] = place()
    if err_out:
        n["onError"] = "continueErrorOutput"
        n["continueOnFail"] = True
        n.setdefault("alwaysOutputData", True)
    return n

# ---------- FRONT: config layer + filters ----------
webhook = scrub(load(V4P, 'Webhook')); set_ids(webhook)
webhook["parameters"]["path"] = "wa-inbound-pcr"
webhook["webhookId"] = newid()
webhook["position"] = place()
NODES.append(webhook)

NODES.append(code_node("Bootstrap Config", C.BOOTSTRAP_CONFIG))

read_config = scrub(load(TPLP, 'Read CONFIG')); set_ids(read_config)
patch_sheets(read_config, "CONFIG"); read_config["position"] = place()
NODES.append(read_config)

NODES.append(code_node("Parse Config", C.PARSE_CONFIG))

# Whitelist Gate (reuse TEMPLATE jsCode as-is)
wg = scrub(load(TPLP, 'Whitelist Gate')); set_ids(wg); wg["position"] = place()
NODES.append(wg)

iffromgroup = scrub(load(V4P, 'If From Group')); set_ids(iffromgroup); iffromgroup["position"] = place()
NODES.append(iffromgroup)
iffromme = scrub(load(V4P, 'IF From Me')); set_ids(iffromme); iffromme["position"] = place()
NODES.append(iffromme)

# Chat Counter (reuse V4 jsCode as-is)
cc = scrub(load(V4P, 'Chat Counter')); set_ids(cc); cc["position"] = place()
NODES.append(cc)

# ---------- USER RESOLVE + BOT MODE ----------
read_user_stats = scrub(load(V4P, 'Read User STATS')); set_ids(read_user_stats)
patch_sheets(read_user_stats, "STATS"); read_user_stats["position"] = place()
NODES.append(read_user_stats)

NODES.append(code_node("Resolve User Row", C.RESOLVE_USER_ROW))

ifbot = scrub(load(V4P, 'IF Bot Mode Active')); set_ids(ifbot); ifbot["position"] = place()
NODES.append(ifbot)

# Rate Limiter LID (reuse V4)
rl = scrub(load(V4P, 'Rate Limiter LID')); set_ids(rl); rl["position"] = place()
NODES.append(rl)

append_buf = scrub(load(V4P, 'Append MSG_BUFFER')); set_ids(append_buf)
patch_sheets(append_buf, "MSG_BUFFER"); append_buf["position"] = place()
NODES.append(append_buf)

# ---------- BUFFER + DEBOUNCE ----------
update_buffer_cols = {
    "No WA": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "debounce_ts": "={{ $('Chat Counter').first().json.process_start_ts }}",
    "lid": "={{ $('Chat Counter').first().json.user_lid }}",
}
update_buffer = scrub(load(V4P, 'Update Buffer')); set_ids(update_buffer)
patch_sheets(update_buffer, "STATS", columns_value=update_buffer_cols, matching=["No WA"], operation="appendOrUpdate")
update_buffer["position"] = place()
NODES.append(update_buffer)

read_hitl = scrub(load(V4P, 'Read STATS for HITL')); set_ids(read_hitl)
patch_sheets(read_hitl, "STATS"); read_hitl["position"] = place()
NODES.append(read_hitl)

hitl = scrub(load(V4P, 'HITL Check')); set_ids(hitl); hitl["position"] = place()
NODES.append(hitl)

wait3 = scrub(load(V4P, 'Wait3')); set_ids(wait3); wait3["webhookId"] = newid(); wait3["position"] = place()
NODES.append(wait3)

reread = scrub(load(V4P, 'Re-Read STATS Debounce')); set_ids(reread)
patch_sheets(reread, "STATS"); reread["position"] = place()
NODES.append(reread)

ifdeb = scrub(load(V4P, 'IF_Chat_Debounce')); set_ids(ifdeb)
# patch baton: timestamp -> debounce_ts
ifdeb_s = json.dumps(ifdeb).replace(".first().json.timestamp", ".first().json.debounce_ts")
ifdeb = json.loads(ifdeb_s); ifdeb["position"] = place()
NODES.append(ifdeb)

read_msgbuf = scrub(load(V4P, 'Read MSG_BUFFER')); set_ids(read_msgbuf)
patch_sheets(read_msgbuf, "MSG_BUFFER"); read_msgbuf["position"] = place()
NODES.append(read_msgbuf)

NODES.append(code_node("Cek_user_status", C.CEK_USER_STATUS))
NODES.append(code_node("Detect Lead Source", C.DETECT_LEAD_SOURCE))
NODES.append(code_node("Preprocess - Context Detection", C.PREPROCESS, per_item=True))

read_faq = scrub(load(V4P, 'Read FAQ')); set_ids(read_faq)
patch_sheets(read_faq, "FAQ"); read_faq["position"] = place()
NODES.append(read_faq)

read_produk = scrub(load(V4P, 'Read PROGRAM Data')); set_ids(read_produk)
read_produk["name"] = "Read PRODUK Data"
patch_sheets(read_produk, "PRODUK"); read_produk["position"] = place()
NODES.append(read_produk)

read_ling = scrub(load(V4P, 'Read ABOUT Data')); set_ids(read_ling)
read_ling["name"] = "Read LINGKUNGAN Data"
patch_sheets(read_ling, "LINGKUNGAN"); read_ling["position"] = place()
NODES.append(read_ling)

read_links = scrub(load(V4P, 'Read LINKS Data')); set_ids(read_links)
patch_sheets(read_links, "LINKS"); read_links["position"] = place()
NODES.append(read_links)

NODES.append(code_node("FAQ Retrieve", C.FAQ_RETRIEVE))

# ---------- AI ----------
anthropic = scrub(load(V4P, 'Anthropic Chat Model')); set_ids(anthropic)
anthropic["credentials"] = {"anthropicApi": dict(ACRED)}
anthropic["parameters"].setdefault("options", {})
anthropic["parameters"]["options"]["maxTokensToSample"] = 768
anthropic["position"] = place()
NODES.append(anthropic)

memory = scrub(load(V4P, 'Simple Memory')); set_ids(memory); memory["position"] = place()
NODES.append(memory)

# System prompt telemarketer: ekstrak blok dari draft md
def extract_prompt():
    path = os.path.join(DRAFT_DIR, '2026-07-15', '2026-07-15-draft-system-prompt-telemarketer.md')
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    marker = txt.split('tempel mulai baris di bawah', 1)[1]
    # blok kode pertama setelah marker
    start = marker.index('```') + 3
    # lewati newline setelah ```
    start = marker.index('\n', start) + 1
    end = marker.index('```', start)
    return marker[start:end].rstrip('\n')

PROMPT = extract_prompt()
ai_agent = scrub(load(TPLP, 'AI Agent')); set_ids(ai_agent)
ai_agent["parameters"]["text"] = "={{ $input.item.json.ai_input_text }}"
ai_agent["parameters"]["options"] = {"systemMessage": "=" + PROMPT}
ai_agent["position"] = place()
NODES.append(ai_agent)

NODES.append(code_node("Process All", C.PROCESS_ALL))

# ---------- BRANCH: MEDIA ----------
# Pola send-message-file: download binary dari URL Drive -> upload multipart ke Kirimi.
# (Ganti pola lama send-message + media_url yg mengirim file sbg dokumen ber-nama URL.)
NODES.append(if_bool("IF Send Media", "={{ $json.isSendMedia }}"))
wait_media = {"parameters": {"amount": 3}, "type": "n8n-nodes-base.wait", "typeVersion": 1.1,
              "position": place(), "id": newid(), "name": "Wait Media", "webhookId": newid()}
NODES.append(wait_media)

# Node 1: Download Media — GET mediaUrl, response = file (binary di field 'data').
# Gagal download (URL mati/bukan publik) -> error output -> Notify Admin Media Error,
# TIDAK kirim apa-apa ke user (balasan teks utama sudah terkirim lebih dulu).
download_media = {
    "parameters": {
        "method": "GET",
        "url": "={{ $('Process All').item.json.mediaUrl }}",
        "options": {"response": {"response": {"responseFormat": "file", "outputPropertyName": "data"}}},
    },
    "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
    "position": place(), "id": newid(), "name": "Download Media",
    "alwaysOutputData": True, "retryOnFail": True, "waitBetweenTries": 2000,
    "continueOnFail": True, "onError": "continueErrorOutput",
}
NODES.append(download_media)

# Node 2: Send Media Kirimi — POST send-message-file, multipart/form-data.
# field 'file' WAJIB binary (dari Download Media). Kredensial di-supply sbg field
# form dari CONFIG (Parse Config) krn custom-auth n8n tak reliabel utk multipart.
send_media = {
    "parameters": {
        "method": "POST",
        "url": "https://api.kirimi.id/v1/send-message-file",
        "sendBody": True,
        "contentType": "multipart-form-data",
        "bodyParameters": {"parameters": [
            {"parameterType": "formData", "name": "user_code", "value": "={{ $('Parse Config').first().json.config.kirimi_user_code }}"},
            {"parameterType": "formData", "name": "secret", "value": "={{ $('Parse Config').first().json.config.kirimi_secret }}"},
            {"parameterType": "formData", "name": "device_id", "value": "={{ $('Parse Config').first().json.config.kirimi_device_id }}"},
            {"parameterType": "formData", "name": "phone", "value": "={{ $('Chat Counter').first().json.user_wa }}"},
            {"parameterType": "formData", "name": "message", "value": "={{ $('Process All').item.json.mediaCaption }}"},
            {"parameterType": "formBinaryData", "name": "file", "inputDataFieldName": "data"},
        ]},
        "options": {},
    },
    "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
    "position": place(), "id": newid(), "name": "Send Media Kirimi",
    "alwaysOutputData": True, "retryOnFail": True, "waitBetweenTries": 2000,
    "continueOnFail": True, "onError": "continueErrorOutput",
}
NODES.append(send_media)
notify_media_err = kirimi_from_template('Notify Admin API Error', 'Notify Admin Media Error',
    message_expr="={{ '🚨 [PCR] Gagal kirim media ' + $('Process All').item.json.mediaKey + ' ke ' + $('Chat Counter').first().json.user_wa }}",
    phone_expr="={{ $('Parse Config').first().json.config.admin_phone }}", err_out=False)
NODES.append(notify_media_err)

# ---------- BRANCH: MEDIA MANUAL (fallback ke tim telemarketer Aar & Aqsa) ----------
# Dipicu saat [SEND_MEDIA] diminta tapi file belum ada di katalog LINKS.
# Tim dikirimi notif WA berisi nomor + nama user + ringkasan permintaan,
# lalu kirim file-nya manual. Otomatis "mati" begitu katalog LINKS terisi.
NODES.append(if_bool("IF Media Manual", "={{ $json.isMediaManual }}"))
NODES.append(code_node("Format Media Notif", C.FORMAT_MEDIA_NOTIF))
notify_media_team = kirimi_from_template('Notify Talk to Sam', 'Notify Media Team',
    message_expr="={{ $json.message }}", phone_expr="={{ $json.phone }}", err_out=False)
notify_media_team["continueOnFail"] = True
notify_media_team["onError"] = "continueRegularOutput"
NODES.append(notify_media_team)

# ---------- BRANCH: SURVEY ----------
NODES.append(if_bool("IF Schedule Survey", "={{ $json.isScheduleSurvey }}"))
write_survey_cols = {
    "no_wa": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "lid": "={{ $('Chat Counter').first().json.user_lid }}",
    "nama": "={{ $('Chat Counter').first().json.user_name }}",
    "tanggal": "={{ $('Process All').item.json.surveyData.tanggal }}",
    "jam": "={{ $('Process All').item.json.surveyData.jam }}",
    "unit_diminati": "={{ $('Process All').item.json.surveyData.unit }}",
    "status": "SCHEDULED",
    "sumber_traffic": "={{ $('Detect Lead Source').first().json.lead_source_final }}",
    "catatan": "",
    "created_ts": "={{ Date.now() }}",
}
write_survey = scrub(load(V4P, 'Record to UNKNOWN')); set_ids(write_survey)
write_survey["name"] = "Write SURVEY"
patch_sheets(write_survey, "SURVEY", columns_value=write_survey_cols, matching=[], operation="append")
write_survey["position"] = place()
NODES.append(write_survey)

update_survey_cols = {
    "No WA": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "lid": "={{ $('Chat Counter').first().json.user_lid }}",
    "survey_date": "={{ $('Process All').item.json.surveyData.tanggal }}",
    "survey_time": "={{ $('Process All').item.json.surveyData.jam }}",
    "survey_status": "SCHEDULED",
    "unit_interest": "={{ $('Process All').item.json.surveyData.unit }}",
    "row_number": 0,
}
update_survey = scrub(load(V4P, 'Update row in sheet')); set_ids(update_survey)
update_survey["name"] = "Update STATS Survey"
patch_sheets(update_survey, "STATS", columns_value=update_survey_cols, matching=["No WA"], operation="update")
update_survey["position"] = place()
NODES.append(update_survey)

NODES.append(code_node("Collect Handover Context", C.COLLECT_HANDOVER))

# Summarize (Basic LLM Chain, non-agent) + model sendiri
anthropic_sum = scrub(load(V4P, 'Anthropic Chat Model')); set_ids(anthropic_sum)
anthropic_sum["name"] = "Anthropic Model Summarize"
anthropic_sum["credentials"] = {"anthropicApi": dict(ACRED)}
anthropic_sum["parameters"].setdefault("options", {})
anthropic_sum["parameters"]["options"]["maxTokensToSample"] = 400
anthropic_sum["parameters"]["options"]["temperature"] = 0.3
anthropic_sum["position"] = place()
NODES.append(anthropic_sum)

summarize = {"parameters": {"promptType": "define", "text": C.SUMMARIZE_PROMPT, "messages": {}},
             "type": "@n8n/n8n-nodes-langchain.chainLlm", "typeVersion": 1.5,
             "position": place(), "id": newid(), "name": "Summarize Handover",
             "onError": "continueRegularOutput"}
NODES.append(summarize)

NODES.append(code_node("Format Handover Message", C.FORMAT_HANDOVER))

notify_field = kirimi_from_template('Notify Talk to Sam', 'Notify Field Team',
    message_expr="={{ $json.message }}", phone_expr="={{ $json.phone }}", err_out=False)
notify_field["continueOnFail"] = True; notify_field["onError"] = "continueRegularOutput"
NODES.append(notify_field)

log_deleg_cols = {
    "no_wa": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "nama": "={{ $('Chat Counter').first().json.user_name }}",
    "event": "DELEGATED",
    "detail": "={{ 'Survey ' + ($('Process All').item.json.surveyData.tanggal || '') + ' ' + ($('Process All').item.json.surveyData.jam || '') + ' unit ' + ($('Process All').item.json.surveyData.unit || '') }}",
    "ts": "={{ Date.now() }}",
}
log_deleg = scrub(load(V4P, 'Record to UNKNOWN')); set_ids(log_deleg)
log_deleg["name"] = "Log EVENTS Delegated"
patch_sheets(log_deleg, "EVENTS", columns_value=log_deleg_cols, matching=[], operation="append")
log_deleg["position"] = place()
NODES.append(log_deleg)

# ---------- BRANCH: REQUEST CALL ----------
NODES.append(if_bool("IF Request Call", "={{ $json.isRequestCall }}"))
log_call_cols = {
    "no_wa": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "nama": "={{ $('Chat Counter').first().json.user_name }}",
    "event": "REQUEST_CALL",
    "detail": "={{ $('Cek_user_status').first().json.user_message_final }}",
    "ts": "={{ Date.now() }}",
}
log_call = scrub(load(V4P, 'Record to UNKNOWN')); set_ids(log_call)
log_call["name"] = "Log Call Request"
patch_sheets(log_call, "EVENTS", columns_value=log_call_cols, matching=[], operation="append")
log_call["position"] = place()
NODES.append(log_call)

# ---------- BRANCH: UNKNOWN ----------
ifunknown = scrub(load(V4P, 'IF Unknown')); set_ids(ifunknown); ifunknown["position"] = place()
NODES.append(ifunknown)
rec_unknown_cols = {
    "Pertanyaan": "={{ $('Cek_user_status').first().json.user_message_final }}",
    "User": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "Tanggal": "={{ new Date().toLocaleString('id-ID', {timeZone: 'Asia/Jakarta'}) }}",
    "message": "={{ $('Process All').item.json.cleanOutput }}",
}
rec_unknown = scrub(load(V4P, 'Record to UNKNOWN')); set_ids(rec_unknown)
patch_sheets(rec_unknown, "UNKNOWN", columns_value=rec_unknown_cols, matching=[], operation="append")
rec_unknown["position"] = place()
NODES.append(rec_unknown)
wait2 = scrub(load(V4P, 'Wait2')); set_ids(wait2); wait2["webhookId"] = newid(); wait2["position"] = place()
NODES.append(wait2)
notify_unknown = kirimi_from_template('Notify Admin Unknown', 'Notify Admin Unknown',
    phone_expr="={{ $('Parse Config').first().json.config.admin_phone }}", err_out=False)
NODES.append(notify_unknown)

# ---------- BRANCH: REPLY (selalu) ----------
wait1 = scrub(load(V4P, 'Wait1')); set_ids(wait1); wait1["webhookId"] = newid(); wait1["position"] = place()
NODES.append(wait1)
reply = kirimi_from_template('Reply Chat Kirimi', 'Reply Chat Kirimi',
    message_expr="={{ $('Process All').item.json.cleanOutput }}",
    phone_expr="={{ $('Chat Counter').first().json.user_wa }}", err_out=True)
reply["retryOnFail"] = True; reply["waitBetweenTries"] = 2000
NODES.append(reply)

check_api = scrub(load(V4P, 'Check API Response')); set_ids(check_api)
check_api["onError"] = "continueErrorOutput"; check_api["position"] = place()
# QA 2026-07-16: override jsCode V4 — flag success:false eksplisit harus dianggap gagal
check_api["parameters"]["jsCode"] = C.CHECK_API_RESPONSE
NODES.append(check_api)

extract_prep = scrub(load(V4P, 'Extract & Prepare Data')); set_ids(extract_prep); extract_prep["position"] = place()
NODES.append(extract_prep)
read_stats = scrub(load(V4P, 'Read STATS')); set_ids(read_stats)
patch_sheets(read_stats, "STATS"); read_stats["position"] = place()
NODES.append(read_stats)
pcm = scrub(load(V4P, 'Process Counter & Merge Data')); set_ids(pcm); pcm["position"] = place()
NODES.append(pcm)

update_stats_cols = {
    "No WA": "={{ $('Resolve User Row').first().json.resolved_key }}",
    "lid": "={{ $json.lid }}",
    "Nama": "={{ $('Process Counter & Merge Data').first().json.Nama }}",
    "Pesan Pertama": "={{ $('Process Counter & Merge Data').first().json['Pesan Pertama'] }}",
    "Counter": "={{ $('Process Counter & Merge Data').first().json.Counter }}",
    "Intensitas Chat": "={{ $('Process Counter & Merge Data').first().json['Intensitas Chat'] }}",
    "Tanggal Chat Pertama": "={{ $('Process Counter & Merge Data').first().json.Tanggal }}",
    "Tanggal Chat Terakhir": "={{ $('Process Counter & Merge Data').first().json.TanggalSekarang }}",
    "Jam Chat Terakhir": "={{ $('Chat Counter').first().json.formatted_time.split(':').slice(0, 2).join(':') }}",
    "last_reply_ts": "={{ Math.floor(Date.now()/1000) }}",
    "unit_interest": "={{ $('Process All').first().json.unit_interest_merged || '' }}",
    "unit_interest_ts": "={{ $('Process All').first().json.unit_changed ? Math.floor(Date.now()/1000) : ($('Resolve User Row').first().json.unit_interest_ts || '') }}",
    "budget_range": "={{ $('Process All').first().json.budget_range_merged || '' }}",
    "budget_range_ts": "={{ $('Process All').first().json.budget_changed ? Math.floor(Date.now()/1000) : ($('Resolve User Row').first().json.budget_range_ts || '') }}",
    "lead_source": "={{ $('Detect Lead Source').first().json.lead_source_final || '' }}",
    "bot_mode": "={{ $('Process All').first().json.isTalkToAdmin ? 'OFF' : 'ON' }}",
}
update_stats = scrub(load(V4P, 'Update to STATS')); set_ids(update_stats)
patch_sheets(update_stats, "STATS", columns_value=update_stats_cols, matching=["No WA"], operation="appendOrUpdate")
update_stats["position"] = place()
NODES.append(update_stats)

del_pending = scrub(load(V4P, 'Delete_Pending_Msg')); set_ids(del_pending)
patch_sheets(del_pending, "STATS"); del_pending["position"] = place()
NODES.append(del_pending)

greet_flag = scrub(load(V4P, 'Update STATS - Greeting Flag')); set_ids(greet_flag); greet_flag["position"] = place()
NODES.append(greet_flag)
if_greet = scrub(load(V4P, 'IF Update Greeting')); set_ids(if_greet); if_greet["position"] = place()
NODES.append(if_greet)
update_greet = scrub(load(V4P, 'Update Greeting')); set_ids(update_greet)
patch_sheets(update_greet, "STATS"); update_greet["position"] = place()
NODES.append(update_greet)

notify_api_err = kirimi_from_template('Notify Admin API Error', 'Notify Admin API Error',
    phone_expr="={{ $('Parse Config').first().json.config.admin_phone }}", err_out=False)
NODES.append(notify_api_err)
del_err = scrub(load(V4P, 'Delete_Pending_Msg_Error')); set_ids(del_err)
patch_sheets(del_err, "STATS"); del_err["position"] = place()
NODES.append(del_err)

# ---------- BRANCH: TALK TO ADMIN ----------
iftalk = scrub(load(V4P, 'IF Talk To Sam')); set_ids(iftalk)
iftalk["name"] = "IF Talk To Admin"
iftalk_s = json.dumps(iftalk).replace("isTalkToSam", "isTalkToAdmin")
iftalk = json.loads(iftalk_s); iftalk["position"] = place()
NODES.append(iftalk)
notify_admin = kirimi_from_template('Notify Talk to Sam', 'Notify Talk to Admin',
    message_expr="={{ '🙋 [PCR] MAU NGOMONG LANGSUNG SAMA TIM:\\n' + $('Chat Counter').item.json.user_wa + '\\n' + $('Chat Counter').item.json.user_name + '\\nPesan: ' + $('Chat Counter').item.json.original_message }}",
    phone_expr="={{ $('Parse Config').first().json.config.admin_phone }}", err_out=False)
NODES.append(notify_admin)
update_row = scrub(load(V4P, 'Update row in sheet')); set_ids(update_row)
patch_sheets(update_row, "STATS"); update_row["position"] = place()
NODES.append(update_row)

# ---------- ERROR paths ----------
reply_err = kirimi_from_template('Reply Error', 'Reply Error',
    phone_expr="={{ $('Chat Counter').first().json.user_wa }}", err_out=False)
NODES.append(reply_err)
del_boff1 = scrub(load(V4P, 'Delete_Pending_Msg_Bot_Off1')); set_ids(del_boff1)
patch_sheets(del_boff1, "STATS"); del_boff1["position"] = place()
NODES.append(del_boff1)

# Notify User Error (append MSG_BUFFER gagal)
notify_user_err = kirimi_from_template('Notify User Error', 'Notify User Error',
    phone_expr="={{ $('Chat Counter').first().json.user_wa }}", err_out=False)
NODES.append(notify_user_err)

# Bot mode OFF stop
del_boff = scrub(load(V4P, 'Delete_Pending_Msg_Bot_Off')); set_ids(del_boff)
patch_sheets(del_boff, "STATS"); del_boff["position"] = place()
NODES.append(del_boff)

# ================= CONNECTIONS =================
edges = [
    ("Webhook", 0, "Bootstrap Config"),
    ("Bootstrap Config", 0, "Read CONFIG"),
    ("Read CONFIG", 0, "Parse Config"),
    ("Parse Config", 0, "Whitelist Gate"),
    ("Whitelist Gate", 0, "If From Group"),
    ("If From Group", 0, "IF From Me"),
    ("IF From Me", 0, "Chat Counter"),
    ("Chat Counter", 0, "Read User STATS"),
    ("Read User STATS", 0, "Resolve User Row"),
    ("Resolve User Row", 0, "IF Bot Mode Active"),
    ("IF Bot Mode Active", 0, "Rate Limiter LID"),
    ("IF Bot Mode Active", 1, "Delete_Pending_Msg_Bot_Off"),
    ("Rate Limiter LID", 0, "Append MSG_BUFFER"),
    ("Append MSG_BUFFER", 0, "Update Buffer"),
    ("Append MSG_BUFFER", 1, "Notify User Error"),
    ("Update Buffer", 0, "Read STATS for HITL"),
    ("Read STATS for HITL", 0, "HITL Check"),
    ("HITL Check", 0, "Wait3"),
    ("Wait3", 0, "Re-Read STATS Debounce"),
    ("Re-Read STATS Debounce", 0, "IF_Chat_Debounce"),
    ("IF_Chat_Debounce", 0, "Read MSG_BUFFER"),
    ("Read MSG_BUFFER", 0, "Cek_user_status"),
    ("Cek_user_status", 0, "Detect Lead Source"),
    ("Detect Lead Source", 0, "Preprocess - Context Detection"),
    ("Preprocess - Context Detection", 0, "Read FAQ"),
    ("Read FAQ", 0, "Read PRODUK Data"),
    ("Read PRODUK Data", 0, "Read LINGKUNGAN Data"),
    ("Read LINGKUNGAN Data", 0, "Read LINKS Data"),
    ("Read LINKS Data", 0, "FAQ Retrieve"),
    ("FAQ Retrieve", 0, "AI Agent"),
    ("AI Agent", 0, "Process All"),
    ("AI Agent", 1, "Reply Error"),
    # branches from Process All
    ("Process All", 0, "IF Send Media"),
    ("Process All", 0, "IF Media Manual"),
    ("Process All", 0, "IF Schedule Survey"),
    ("Process All", 0, "IF Request Call"),
    ("Process All", 0, "IF Unknown"),
    ("Process All", 0, "Wait1"),
    ("Process All", 0, "IF Talk To Admin"),
    # media (send-message-file: download binary -> upload multipart)
    ("IF Send Media", 0, "Wait Media"),
    ("Wait Media", 0, "Download Media"),
    ("Download Media", 0, "Send Media Kirimi"),
    ("Download Media", 1, "Notify Admin Media Error"),
    ("Send Media Kirimi", 1, "Notify Admin Media Error"),
    # media manual (fallback notif ke tim Aar & Aqsa)
    ("IF Media Manual", 0, "Format Media Notif"),
    ("Format Media Notif", 0, "Notify Media Team"),
    # survey
    ("IF Schedule Survey", 0, "Write SURVEY"),
    ("Write SURVEY", 0, "Update STATS Survey"),
    ("Update STATS Survey", 0, "Collect Handover Context"),
    ("Collect Handover Context", 0, "Summarize Handover"),
    ("Summarize Handover", 0, "Format Handover Message"),
    ("Format Handover Message", 0, "Notify Field Team"),
    ("Notify Field Team", 0, "Log EVENTS Delegated"),
    # request call
    ("IF Request Call", 0, "Log Call Request"),
    # unknown
    ("IF Unknown", 0, "Record to UNKNOWN"),
    ("Record to UNKNOWN", 0, "Wait2"),
    ("Wait2", 0, "Notify Admin Unknown"),
    # reply
    ("Wait1", 0, "Reply Chat Kirimi"),
    ("Reply Chat Kirimi", 0, "Check API Response"),
    ("Reply Chat Kirimi", 1, "Notify Admin API Error"),
    ("Check API Response", 0, "Extract & Prepare Data"),
    ("Check API Response", 0, "Delete_Pending_Msg"),
    ("Check API Response", 0, "Update STATS - Greeting Flag"),
    ("Check API Response", 1, "Notify Admin API Error"),
    ("Extract & Prepare Data", 0, "Read STATS"),
    ("Read STATS", 0, "Process Counter & Merge Data"),
    ("Process Counter & Merge Data", 0, "Update to STATS"),
    ("Update STATS - Greeting Flag", 0, "IF Update Greeting"),
    ("IF Update Greeting", 0, "Update Greeting"),
    ("Notify Admin API Error", 0, "Delete_Pending_Msg_Error"),
    # talk to admin
    ("IF Talk To Admin", 0, "Notify Talk to Admin"),
    ("Notify Talk to Admin", 0, "Update row in sheet"),
    # error
    ("Reply Error", 0, "Delete_Pending_Msg_Bot_Off1"),
]
# AI sub-node edges (type ai_languageModel / ai_memory)
ai_edges = [
    ("Anthropic Chat Model", "ai_languageModel", "AI Agent"),
    ("Simple Memory", "ai_memory", "AI Agent"),
    ("Anthropic Model Summarize", "ai_languageModel", "Summarize Handover"),
]

def build_connections(edges, ai_edges):
    conn = {}
    # group by source
    maxidx = {}
    for src, idx, tgt in edges:
        maxidx[src] = max(maxidx.get(src, 0), idx)
    for src, idx, tgt in edges:
        conn.setdefault(src, {}).setdefault("main", [])
        main = conn[src]["main"]
        while len(main) <= idx:
            main.append([])
        main[idx].append({"node": tgt, "type": "main", "index": 0})
    for src, typ, tgt in ai_edges:
        conn.setdefault(src, {}).setdefault(typ, [[]])
        conn[src][typ][0].append({"node": tgt, "type": typ, "index": 0})
    return conn

CONNECTIONS = build_connections(edges, ai_edges)

MAIN_WF = {
    "name": "VIRA-PCR Main",
    "nodes": NODES,
    "connections": CONNECTIONS,
    "active": False,
    "settings": {"executionOrder": "v1", "timezone": "Asia/Jakarta", "callerPolicy": "workflowsFromSameOwner"},
    "pinData": {},
    "tags": [],
}

# ================= FILE 2 & 3 =================
def build_buffer_cleanup():
    wf = load_json(os.path.join(DRAFT_DIR, '..', 'the scholars', 'report', 'production', '2026-07-03-VIRA_MSG_BUFFER-cleanup.json'))
    wf["name"] = "VIRA-PCR - MSG_BUFFER Cleanup (harian 03:00 WIB)"
    for n in wf["nodes"]:
        if n["type"] == "n8n-nodes-base.googleSheets":
            n["parameters"]["documentId"] = {"__rl": True, "value": SHEET_ID_EXPR2, "mode": "id"}
            n["credentials"] = {"googleApi": dict(GCRED)}
        n["id"] = newid()
    return wf

# Buffer cleanup & error need their own Bootstrap? Cleanup uses schedule trigger, no Bootstrap Config.
# -> pakai placeholder expression tak berlaku (tak ada Bootstrap Config). Gunakan placeholder string literal.
SHEET_ID_EXPR2 = "PASTE_PCR_GOOGLE_SHEET_ID_HERE"

def load_json(p):
    with open(p, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def build_buffer_cleanup2():
    src = os.path.join(OUT_DIR, '..', '..', 'the scholars', 'report', 'production', '2026-07-03-VIRA_MSG_BUFFER-cleanup.json')
    src = os.path.normpath(src)
    wf = load_json(src)
    wf["name"] = "VIRA-PCR - MSG_BUFFER Cleanup (harian 03:00 WIB)"
    s = json.dumps(wf, ensure_ascii=False)
    s = s.replace("1tEJYayS0pQTVO2FI9xO363nQBkjFz5TL5u0-zsa-CwE", SHEET_ID_EXPR2)
    s = s.replace("3gTKMbD8lJDLbRqR", GCRED["id"])
    s = s.replace("Google Service Account thescholars", GCRED["name"])
    s = s.replace("The_Scholars_Database", "PCR_Database").replace("thescholars", "pcr")
    wf = json.loads(s)
    for n in wf["nodes"]:
        n["id"] = newid()
        p = n.get("parameters", {})
        if "documentId" in p:
            p["documentId"] = {"__rl": True, "value": SHEET_ID_EXPR2, "mode": "id"}
            n["credentials"] = {"googleApi": dict(GCRED)}
    return wf

def build_error_notifier():
    src = os.path.join(OUT_DIR, '..', '..', 'the scholars', 'report', 'production', '2026-07-02-VIRA_V4-error-workflow.json')
    src = os.path.normpath(src)
    wf = load_json(src)
    wf["name"] = "VIRA-PCR Error Notifier"
    for n in wf["nodes"]:
        n["id"] = newid()
        if n["type"] == "n8n-nodes-base.httpRequest":
            # ubah ke pola httpCustomAuth (buang user_code/secret/device_id plaintext)
            params = n["parameters"]
            plist = params.get("bodyParameters", {}).get("parameters", [])
            new_plist = []
            for it in plist:
                if it["name"] in ("user_code", "secret", "device_id"):
                    continue
                if it["name"] == "phone":
                    it["value"] = "{{ADMIN_PHONE}}"
                new_plist.append(it)
            params["bodyParameters"]["parameters"] = new_plist
            params["authentication"] = "genericCredentialType"
            params["genericAuthType"] = "httpCustomAuth"
            n["credentials"] = {"httpCustomAuth": dict(KCRED)}
        if n["type"] == "n8n-nodes-base.code":
            n["parameters"]["jsCode"] = n["parameters"]["jsCode"].replace("[${wfName}]", "[PCR ${wfName}]")
    # scrub sisa
    s = json.dumps(wf, ensure_ascii=False).replace("VIRA]", "PCR]").replace("thescholars", "pcr").replace("Scholars", "PCR")
    wf = json.loads(s)
    return wf

# ================= WRITE =================
def dump(obj, name):
    path = os.path.join(OUT_DIR, name)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    return path

# Output MAIN sebagai file 2026-07-17 (JANGAN timpa 2026-07-15 / 2026-07-16).
p1 = dump(MAIN_WF, '2026-07-17-VIRA-PCR-main.json')
print("WROTE:", p1)
print("MAIN nodes:", len(MAIN_WF["nodes"]))

# Buffer cleanup & error notifier tidak berubah untuk update 2026-07-16 dan
# sumbernya (produksi The Scholars) di luar repo ini. Regenerasi hanya bila
# file sumber tersedia; kalau tidak, lewati (pakai file 2026-07-15 yang ada).
try:
    p2 = dump(build_buffer_cleanup2(), '2026-07-17-VIRA-PCR-buffer-cleanup.json'); print("WROTE:", p2)
except Exception as e:
    print("SKIP buffer-cleanup (sumber tak tersedia):", e)
try:
    p3 = dump(build_error_notifier(), '2026-07-17-VIRA-PCR-error-notifier.json'); print("WROTE:", p3)
except Exception as e:
    print("SKIP error-notifier (sumber tak tersedia):", e)
