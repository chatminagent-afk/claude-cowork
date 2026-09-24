
// Cek apakah Kirimi API sukses
const input = $input.first();
const responseData = input.json;

// Kirimi API return success jika ada field 'status' = true atau 'data'
const isSuccess = responseData.status === true || 
                  responseData.success === true ||
                  (responseData.data && responseData.data.id) ||
                  (responseData.message && responseData.message !== 'error');

if (!isSuccess) {
  console.log('❌ Kirimi API Response Error:', JSON.stringify(responseData));
  throw new Error('Kirimi API gagal: ' + JSON.stringify(responseData));
}

console.log('✅ Kirimi API sukses:', JSON.stringify(responseData));
return [input];

