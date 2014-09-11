#!/usr/local/bin/python
#
# File:         warpfsl2itk.py
# Last changed: 9/11/2014
# Dependence:   nibabel, numpy
# Author:       Joo-won Kim
# MIT license (opensource.org/licenses/MIT)
#
# TEST VERSION
# Convert FSL warp Nifti1 file to ITK(ANTs, Spinal Cord Toolbox) file.
#
# Usage: (python) warpfsl2itk.py input output
#

import nibabel as nib
import numpy as np
import sys

input_filename = 'fullWarp_rel.nii.gz'
output_filename = 'fullWarp_itk.nii.gz'

if len(sys.argv) == 1:
	pass
elif len(sys.argv) == 2:
	input_filename = sys.argv[1]
	if input_filename[-7:] == '.nii.gz':
		output_filename = input_filename[:-7] + '_itk.nii.gz'
	elif input_filename[-4:] == '.nii':
		output_filename = input_filename[:-4] + '_itk.nii'
	else:
		output_filename = input_filename + '_itk.nii.gz'
else:
	input_filename = sys.argv[1]
	output_filename = sys.argv[2]

img = nib.load( input_filename )

hdr = img.get_header()
hdr.set_intent('vector')

dat = img.get_data()
shp = list(dat.shape)
if len(shp) != 4:
	print 'Input shape %s is wrong.' % dat.shape

shp.insert(3,1)
dat_new = np.ndarray( shp, dtype=float )
#dat_new[..., 0, ...] = dat.copy()

# fsl    itk
#  i  ->  R
#  j  ->  A
#  k  ->  I

# input orientation
# IS THIS A RIGHT, CORRECT WAY?
srow = np.array( [ hdr['srow_x'], hdr['srow_y'], hdr['srow_z'] ] )
srow_abs = np.abs( srow )
indexL = srow_abs[0,0:3].argmax()
indexP = srow_abs[1,0:3].argmax()
indexI = srow_abs[2,0:3].argmax()
signL = np.sign( srow[0,indexL] )
signP = np.sign( srow[1,indexP] )
signI = np.sign( srow[2,indexI] )

orientation = ['L','P','I']
if signL > 0:
	orientation[indexL] = 'L'
else:
	orientation[indexL] = 'R'
if signP > 0:
	orientation[indexP] = 'P'
else:
	orientation[indexP] = 'A'
if signI > 0:
	orientation[indexI] = 'I'
else:
	orientation[indexI] = 'S'
print 'Input Orientatoin : %s' % "".join(orientation)

dat_new[..., 0, 0] = -signL * dat[..., indexL]
dat_new[..., 0, 1] = -signP * dat[..., indexP]
dat_new[..., 0, 2] =  signI * dat[..., indexI]


img_new = nib.Nifti1Image( dat_new, img.get_affine(), hdr );
nib.save( img_new, output_filename )

