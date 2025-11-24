import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

export function useEmotionSupport(learnerId, quizSessionId) {
  const [supportWidget, setSupportWidget] = useState(null)
  const [isCheckingIntervention, setIsCheckingIntervention] = useState(false)

  const checkIntervention = useCallback(async () => {
    if (isCheckingIntervention || !learnerId) return

    setIsCheckingIntervention(true)
    try {
      const res = await axios.post(
        `http://localhost:8000/api/emotion-support/check-intervention/${learnerId}`,
        null,
        { params: { quiz_session_id: quizSessionId } }
      )

      if (res.data.should_intervene) {
        setSupportWidget({
          intervention: res.data.intervention,
          supportMessage: res.data.support_message,
          decision: res.data.decision
        })
      }
    } catch (error) {
      console.error('Error checking intervention:', error)
    } finally {
      setIsCheckingIntervention(false)
    }
  }, [learnerId, quizSessionId, isCheckingIntervention])

  const dismissWidget = () => {
    setSupportWidget(null)
  }

  const submitFeedback = async (interventionId, wasHelpful, actionTaken) => {
    try {
      await axios.post('http://localhost:8000/api/emotion-support/intervention-feedback', {
        intervention_id: interventionId,
        was_helpful: wasHelpful,
        action_taken: actionTaken
      })
    } catch (error) {
      console.error('Error submitting feedback:', error)
    }
  }

  return {
    supportWidget,
    checkIntervention,
    dismissWidget,
    submitFeedback
  }
}