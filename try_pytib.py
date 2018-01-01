from pytib import Segment


sentence = ' སྙན་ངག་མེ་ལོང་མ ཕ་མའི་སློབ་གསོའམ་\nཡང་ན་ཁྱིམ་གྱི་སློབ་གསོའི་གན'
truc = Segment()
truc.include_user_vocab()
segmented = truc.segment(sentence, reinsert_aa=False, space_at_punct=True, distinguish_ra_sa=True, affix_particles=True)
print(segmented)
