import MeCab
tagger = MeCab.Tagger("-Owakati")
print(tagger.parse("猫の飼い方と餌のあげ方"))
