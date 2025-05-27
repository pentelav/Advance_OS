import threading
import sys
import os
from collections import defaultdict
import time

class WordCounter:
    def __init__(self, filename, num_segments):
        self.filename = filename
        self.num_segments = num_segments
        self.file_size = os.path.getsize(filename)
        self.segment_size = self.file_size // num_segments
        self.lock = threading.Lock()
        self.threads = []
        self.global_word_count = defaultdict(int)
        self.thread_results = []

    def process_segment(self, segment_num, start_pos, end_pos):
        local_word_count = defaultdict(int)
        current_word = []
        
        with open(self.filename, 'r', encoding='utf-8') as file:
            # Adjust start position to the beginning of a word
            if start_pos != 0:
                file.seek(start_pos - 1)
                prev_char = file.read(1)
                file.seek(start_pos)
                # If we're in the middle of a word, read until word boundary
                if prev_char not in [' ', '\n', '\t', '\r', '\x0b', '\x0c']:
                    while True:
                        char = file.read(1)
                        start_pos += 1
                        if not char or char in [' ', '\n', '\t', '\r', '\x0b', '\x0c']:
                            break
            
            file.seek(start_pos)
            # If we've gone past the end position, skip this segment
            if start_pos >= end_pos:
                self.thread_results.append((segment_num, dict(local_word_count)))
                return
            
            # Read until end position
            while file.tell() < end_pos:
                char = file.read(1)
                if not char:
                    break
                
                if char.isalpha() or char == "'":
                    current_word.append(char.lower())
                else:
                    if current_word:
                        word = ''.join(current_word)
                        local_word_count[word] += 1
                        current_word = []
            
            # Add the last word if file ends without a separator
            if current_word:
                word = ''.join(current_word)
                local_word_count[word] += 1
        
        # Store thread result
        with self.lock:
            self.thread_results.append((segment_num, dict(local_word_count)))

    def run(self):
        # Create and start threads
        for i in range(self.num_segments):
            start_pos = i * self.segment_size
            end_pos = (i + 1) * self.segment_size if i != self.num_segments - 1 else self.file_size
            thread = threading.Thread(target=self.process_segment, args=(i, start_pos, end_pos))
            self.threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()
        
        # Combine results from all threads
        for segment_num, word_count in self.thread_results:
            for word, count in word_count.items():
                self.global_word_count[word] += count
        
        # Print intermediate results
        print("\nIntermediate Thread Results:")
        for segment_num, word_count in sorted(self.thread_results, key=lambda x: x[0]):
            print(f"\nThread {segment_num} word counts:")
            for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"{word}: {count}")
        
        # Print final consolidated result
        print("\nFinal Consolidated Word Counts (Top 20):")
        for word, count in sorted(self.global_word_count.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"{word}: {count}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python word_counter.py <filename> <num_segments>")
        return
    
    filename = sys.argv[1]
    num_segments = int(sys.argv[2])
    
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' not found.")
        return
    
    if num_segments < 1:
        print("Error: Number of segments must be at least 1.")
        return
    
    print(f"Processing file '{filename}' into {num_segments} segments...")
    
    start_time = time.time()
    counter = WordCounter(filename, num_segments)
    counter.run()
    
    print(f"\nTotal processing time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()