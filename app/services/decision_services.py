def auto_approve_band(score):
    return score >= 85


def auto_reject_band(score):
    return score < 50


def manual_review_band(score):
    return 50 <= score < 85


def get_reason_codes(face, live, doc, fraud):
    reasons = []
    if face < 70:
        reasons.append("face_mismatch")
    if live < 70:
        reasons.append("liveness_failure")
    if doc < 70:
        reasons.append("doc_expired")
    if fraud > 70:
        reasons.append("fraud_score_high")
    return ",".join(reasons) if reasons else "OK"


def get_decision_state(overall, fraud):
    if fraud > 80:
        return "rejected"

    if auto_approve_band(overall):
        return "approved"

    if manual_review_band(overall):
        return "manual_review"

    return "retry"


def evaluate_case(face_score, live_score, doc_score, fraud_score):
    overall_score = round((face_score + live_score + doc_score) / 3, 2)
    reason_codes = get_reason_codes(face_score, live_score, doc_score, fraud_score)
    decision_state = get_decision_state(overall_score, fraud_score)

    return {
        "overall_score": overall_score,
        "reason_codes": reason_codes,
        "decision_state": decision_state
    }
