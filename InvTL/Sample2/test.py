'Class :P:'
'Update :0:'
_DP_P_self__receive_messages_0 = set()
'Update :1:'
_DP_P_self_q = set()
'Update :2:'
_DP_P_self_s = set()
'Update :3:'
_DP_P_self_s.add(_e_ps)
'Update :4:'
reqc = _DP_P_self_logical_clock()
'Update :5:'
_DP_P_self_q.add((reqc, _DP_P_self__id))
'Update :6:'
_DP_P_self_q.remove((reqc, _DP_P_self__id))
'Update :7:'
_DP_P_self_q.add((reqts, _source))
'Update :8:'
_DP_P_self_q.remove((time, _source))
'Update :9:'
_DP_P_self__receive_messages_0.add((_c3, _p3))
'Query :0:'

def x():
    (not (( (set((c2, p2) for (c2, p2) in _DP_P_self_q if (not (p2 == _DP_P_self__id))) == set()) or  ((reqc, _DP_P_self__id) < min(set((c2, p2) for (c2, p2) in _DP_P_self_q if (not (p2 == _DP_P_self__id)))))) and ( len(set(c3 for p3 in _DP_P_self_s for (c3, p3_) in _DP_P_self__receive_messages_0 if (p3_ == p3) if (c3 > reqc))) == len(_DP_P_self_s))))
