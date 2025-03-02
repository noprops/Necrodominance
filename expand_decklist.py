# まずデッキリストを読み込む
deck = []
with open('Necrodominance.txt', 'r') as file:
    for line in file:
        # Stop reading at empty line (before sideboard)
        if line.strip() == "":
            break
        
        # Get count and card name from each line
        count, *card_name = line.strip().split(' ')
        card_name = ' '.join(card_name)
        # Add cards to deck
        deck.extend([card_name] * int(count))

# 展開したデッキリストを新しいファイルに保存
with open('expanded_decklist.txt', 'w') as file:
    for card in deck:
        file.write(f"{card}\n")