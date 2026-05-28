const express = require('express');
const OpenAI = require('openai');

const router = express.Router();

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// 대화 히스토리는 메모리에 세션 ID로 관리 (간단 버전)
const sessions = new Map();

// POST /api/chat
router.post('/', async (req, res) => {
  const { message, sessionId, systemPrompt } = req.body;

  if (!message) {
    return res.status(400).json({ error: 'message 필드가 필요합니다.' });
  }

  const sid = sessionId || 'default';

  if (!sessions.has(sid)) {
    sessions.set(sid, [
      {
        role: 'system',
        content: systemPrompt || '당신은 KDN(한국전력 자회사)의 친절한 AI 어시스턴트입니다. 사용자의 질문에 명확하고 간결하게 답변해주세요.',
      },
    ]);
  }

  const history = sessions.get(sid);
  history.push({ role: 'user', content: message });

  try {
    const completion = await openai.chat.completions.create({
      model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
      messages: history,
    });

    const reply = completion.choices[0].message;
    history.push(reply);

    res.json({
      reply: reply.content,
      sessionId: sid,
      usage: completion.usage,
    });
  } catch (err) {
    console.error('OpenAI error:', err.message);
    res.status(500).json({ error: 'AI 응답 중 오류가 발생했습니다.', detail: err.message });
  }
});

// DELETE /api/chat/:sessionId - 대화 초기화
router.delete('/:sessionId', (req, res) => {
  sessions.delete(req.params.sessionId);
  res.json({ message: '대화가 초기화되었습니다.' });
});

// GET /api/chat/:sessionId - 대화 히스토리 조회
router.get('/:sessionId', (req, res) => {
  const history = sessions.get(req.params.sessionId) || [];
  res.json({ sessionId: req.params.sessionId, history });
});

module.exports = router;
