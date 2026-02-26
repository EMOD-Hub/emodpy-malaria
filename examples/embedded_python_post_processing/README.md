# Malaria_Sim Example with Embedded Python Post-Processing (EP4)

Things to notice in this demo:

1) **EP4/dtk_post_process.py script** This script does very little but hopefully just enough to prove the point. It reads the InsetChart.json output file, calculates a summary statistic (in this case the  sum total of all adult vectors, just because), and then deletes the original output file.  This is intended to demonstrate how a post-proc script can do a data reduction operation. From the end user's point of view, it's like the larger output file was never here.
2) **EP4/dtk_pre_process.py script**. This actually does nothing except a couple of imports and it turns out that this is necessary if we want to import these modules in the post script. This is a known bug with a simple workaround for now.
3) **dtk_centos.id**. Note that we use Singularity for this example. We actually want to move all examples and scenarios to Singularity, so consider this the new normal. There is a line in example.py (set_sif) that makes this happen. The Singularity Image File we are using already exists in COMPS as an Asset Collection. This one has emod-api, numpy, and pandas installed. We will be providing a URL with instructions for how to create your own SIF if you need a different runtime environment. This is a simple process once one has a few instructions.
4) **requirements.txt**. Most examples don't have their own requirementst.txt but this does because it turns out we need a particular emod-malaria because we need a particular Eradication. This is because of a bamboo build issue in which some Malaria-Ongoing build plans are producing binaries that are not linked against the python (dev) lib. Until this is fixed, we are limited in terms of which binaries will work for EP4.

