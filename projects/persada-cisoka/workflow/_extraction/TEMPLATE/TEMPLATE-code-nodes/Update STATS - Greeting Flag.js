// ====================================================================
// UPDATE GREETING FLAG - ROBUST ALTERNATIVE
// ====================================================================
// This version uses pattern matching instead of exact keywords
// More flexible and covers any future variations

const processedData = $('Process All').first().json;
const cleanOutput = (processedData.cleanOutput || '').toLowerCase();
const shouldAskStatus = $('Cek_user_status').first().json.should_ask_status || false;
const chatCounter = $('Chat Counter').first().json;

// Check if output is asking about parent vs student
// Pattern: mentions both "orang tua" (or variants) AND "anak" (or variants) in question form
const hasParentReference = /orang\s*tua|ortu|bapak|ibu/.test(cleanOutput);
const hasStudentReference = /anak|murid|calon/.test(cleanOutput);
const isQuestion = /\?|ya\s*$/.test(cleanOutput); // Ends with ? or "ya"

const isStatusQuestion = hasParentReference && hasStudentReference && isQuestion;

// Alternative check: looks like first contact greeting
const hasGreeting = /halo|hai|terima kasih/.test(cleanOutput);
const isLikelyStatusQuestion = hasGreeting && isStatusQuestion;

// Update flag if this is status question
if (shouldAskStatus) {
  console.log(`📝 [GREETING SENT] Marking greeting_sent = Y for user ${chatCounter.user_wa}`);
  console.log(`📝 Detected status question pattern in: ${cleanOutput.substring(0, 100)}...`);
  console.log(`   Pattern matched: hasParent=${hasParentReference}, hasStudent=${hasStudentReference}, isQuestion=${isQuestion}`);
  
  return [{
    json: {
      user_wa: chatCounter.user_wa,
      user_lid: chatCounter.user_lid,
      greeting_sent: 'Y',
      update_needed: true
    }
  }];
} else {
  console.log('ℹ️ Not a status question');
  console.log(`   shouldAskStatus: ${shouldAskStatus}`);
  console.log(`   hasParentRef: ${hasParentReference}, hasStudentRef: ${hasStudentReference}, isQuestion: ${isQuestion}`);
  console.log(`   Output: ${cleanOutput.substring(0, 100)}`);
  
  return [{
    json: {
      update_needed: false
    }
  }];
}
