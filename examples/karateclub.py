import networkx as nx
import pandas as pd
import imageio
import matplotlib.pyplot as plt
import tqdm
import pathlib

from sse import SimilarityEmbedder

def animate(labelsnp,all_embeddings,mask):
    labelsnp = labelsnp[mask]

    for i,embedding in enumerate(tqdm.tqdm(all_embeddings)):
        data = embedding[mask]
        fig = plt.figure(dpi=150)
        fig.clf()
        ax = fig.subplots()
        plt.title('Epoch {}'.format(i))

        colormap = ['r' if l=='Administrator' else 'b' for l in labelsnp]
        plt.scatter(data[:,0],data[:,1], c=colormap)

        ax.annotate('Administrator',(data[0,0],data[0,1]))
        ax.annotate('Instructor',(data[33,0],data[33,1]))

        plt.savefig('./ims/{n}.png'.format(n=i))
        plt.close()

    imagep = pathlib.Path('./ims/')
    images = imagep.glob('*.png')
    images = list(images)
    images.sort(key=lambda x : int(str(x).split('/')[-1].split('.')[0]))
    with imageio.get_writer('./animation.gif', mode='I') as writer:
        for image in images:
            data = imageio.imread(image.__str__())
            writer.append_data(data)

if __name__=='__main__':
	edges = nx.to_pandas_edgelist(nx.karate_club_graph())
	nodes = pd.read_csv('./karate_attributes.csv')

	sage = SimilarityEmbedder(2,distance='l2')
	sage.add_data(edges,nodes,nodeid='node',classid='community')

	t5, t1 = sage.evaluate()
	print(f'Untrained network performance: top 5 {t5}, top1 {t1}')

	epochs, batch_size = 150, 15
	_,_,_,all_embeddings = sage.train(epochs, batch_size, unsupervised = True, learning_rate=1e-2, test_every_n_epochs=10, return_intermediate_embeddings=True)

	print(sage.query_neighbors([0,33],k=33))
	#sage.start_api()
	animate(sage.labels,all_embeddings,sage.entity_mask)
