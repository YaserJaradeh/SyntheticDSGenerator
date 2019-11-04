import random
from datetime import datetime, timedelta
import namegenerator

adjectives = ["admiring","adoring","affectionate","agitated","amazing","angry","awesome","beautiful","blissful","bold","boring","brave","busy","charming","clever","cool","compassionate","competent","condescending","confident","cranky","crazy","dazzling","determined","distracted","dreamy","eager","ecstatic","elastic","elated","elegant","eloquent","epic","exciting","fervent","festive","flamboyant","focused","friendly","frosty","funny","gallant","gifted","goofy","gracious","great","happy","hardcore","heuristic","hopeful","hungry","infallible","inspiring","interesting","intelligent","jolly","jovial","keen","kind","laughing","loving","lucid","magical","mystifying","modest","musing","naughty","nervous","nice","nifty","nostalgic","objective","optimistic","peaceful","pedantic","pensive","practical","priceless","quirky","quizzical","recursing","relaxed","reverent","romantic","sad","serene","sharp","silly","sleepy","stoic","strange","stupefied","suspicious","sweet","tender","thirsty","trusting","unruffled","upbeat","vibrant","vigilant","vigorous","wizardly","wonderful","xenodochial","youthful","zealous","zen"]
surenames = ["albattani","allen","almeida","antonelli","agnesi","archimedes","ardinghelli","aryabhata","austin","babbage","banach","banzai","bardeen","bartik","bassi","beaver","bell","benz","bhabha","bhaskara","black","blackburn","blackwell","bohr","booth","borg","bose","bouman","boyd","brahmagupta","brattain","brown","buck","burnell","cannon","carson","cartwright","cerf","chandrasekhar","chaplygin","chatelet","chatterjee","chebyshev","cohen","chaum","clarke","colden","cori","cray","curie","darwin","davinci","dewdney","dhawan","diffie","dijkstra","dirac","driscoll","dubinsky","easley","edison","einstein","elbakyan","elgamal","elion","ellis","engelbart","euclid","euler","faraday","feistel","fermat","fermi","feynman","franklin","gagarin","galileo","galois","ganguly","gates","gauss","germain","goldberg","goldstine","goldwasser","golick","goodall","gould","greider","grothendieck","haibt","hamilton","haslett","hawking","hellman","heisenberg","hermann","herschel","hertz","heyrovsky","hodgkin","hofstadter","hoover","hopper","hugle","hypatia","ishizaka","jackson","jang","jennings","jepsen","johnson","joliot","jones","kalam","kapitsa","kare","keldysh","keller","kepler","khayyam","khorana","kilby","kirch","knuth","kowalevski","lalande","lamarr","lamport","leakey","leavitt","lederberg","lehmann","lewin","lichterman","liskov","lovelace","lumiere","mahavira","margulis","matsumoto","maxwell","mayer","mccarthy","mcclintock","mclaren","mclean","mcnulty","mendel","mendeleev","meitner","meninsky","merkle","mestorf","mirzakhani","moore","morse","murdock","moser","napier","nash","neumann","newton","nightingale","nobel","noether","northcutt","noyce","panini","pare","pascal","pasteur","payne","perlman","pike","poincare","poitras","proskuriakova","ptolemy","raman","ramanujan","ride","montalcini","ritchie","rhodes","robinson","roentgen","rosalind","rubin","saha","sammet","sanderson","satoshi","shamir","shannon","shaw","shirley","shockley","shtern","sinoussi","snyder","solomon","spence","stonebraker","sutherland","swanson","swartz","swirles","taussig","tereshkova","tesla","tharp","thompson","torvalds","tu","turing","varahamihira","vaughan","visvesvaraya","volhard","villani","wescoff","wilbur","wiles","williams","williamson","wilson","wing","wozniak","wright","wu","yalow","yonath","zhukovsky"]


class Markov(object):
	def __init__(self, open_file):
		self.cache = {}
		self.open_file = open_file
		self.words = self.file_to_words()
		self.word_size = len(self.words)
		self.database()

	def file_to_words(self):
		self.open_file.seek(0)
		data = self.open_file.read()
		words = data.split()
		return words

	def triples(self):
		""" Generates triples from the given data string. So if our string were
				"What a lovely day", we'd generate (What, a, lovely) and then
				(a, lovely, day).
		"""
		
		if len(self.words) < 3:
			return
		
		for i in range(len(self.words) - 2):
			yield (self.words[i], self.words[i+1], self.words[i+2])
			
	def database(self):
		for w1, w2, w3 in self.triples():
			key = (w1, w2)
			if key in self.cache:
				self.cache[key].append(w3)
			else:
				self.cache[key] = [w3]
				
	def generate_markov_text(self, size=25):
		seed = random.randint(0, self.word_size-3)
		seed_word, next_word = self.words[seed], self.words[seed+1]
		w1, w2 = seed_word, next_word
		gen_words = []
		for i in range(size):
			gen_words.append(w1)
			w1, w2 = w2, random.choice(self.cache[(w1, w2)])
		gen_words.append(w2)
		return ' '.join(gen_words)


hmm = Markov(open('./data/jeeves.txt'))


def get_random_name():
	left_index = random.randrange(len(adjectives))
	right_index = random.randrange(len(surenames))
	return f'{adjectives[left_index]} {surenames[right_index]}'


def get_random_text(length=25):
	return hmm.generate_markov_text(length)


def get_random_title():
	return f"{namegenerator.gen().replace('-', ' ')} {namegenerator.gen().replace('-', ' ')}"


def get_random_datetime(min_year=1990, max_year=datetime.now().year):
	# generate a datetime in format yyyy-mm-dd hh:mm:ss.000000
	start = datetime(min_year, 1, 1, 00, 00, 00)
	years = max_year - min_year + 1
	end = start + timedelta(days=365 * years)
	return (start + (end - start) * random.random()).strftime("%Y-%m-%dT%H:%M:%S.%f")
