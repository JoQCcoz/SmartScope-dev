SmartScope test commands
========================

It is possible to test the SmartScope installation and setup by running the workflow without the microscope.

The initial database provided with SmartScope should already contain a fake_scope and fake_detector for selection.

Selecting this scope during a `session setup <../run_smartscope/runsmartscope.html>`_ will pick random images from a bank of images.


Testing the connection to serialEM
##################################

To quickly test if your settings are good for the python connection to SerialEM, you can use the following commands and replace IP by the gatan PC address and port by 48888.

From our examples above, the Talos Arctica IP would be 192.168.0.32 and port would be 48888.

.. code-block::

    docker exec smartscope smartscope.py test_serialem_connection IP port

    ### EXAMPLE ###
    docker exec smartscope smartscope.py test_serialem_connection 192.138.0.32 48888

If the connection is successful, a :code:`Hello from smartscope` message should appear in the SerialEM log window. Now, you can proceed to adding a microscope.

Refining LM pixel sizes (Added to dev branch on 20220721)
#########################################################

It may happen that SmartScope doesn't image the squares or holes precisely. The problem may be related to the calibrations in the LM range of magnifications.
The two main calibrations that are used by SmartScope are :code:`PixelSpacing` and :code:`RotationAngle`.
We have included a procedure to calculate the PixelSpacing from grids that were already sampled.

.. code-block::

    docker exec smartscope smartscope.py refine_pixel_size grid_id_1,grid_id_2,...

    ### EXAMPLE ###
    docker exec smartscope smartscope.py refine_pixel_size 2AR1-0504_1jqOS0wc36dznzLwuYOO

    ###################  Atlas magnification  ###################
    Calculated pixel size: 655.4 +/- 0.0 A/pix (n= 1).
    This is an difference of 2 % from the current 644.2 A/pix value.
    #############################################################

    ###################  Square magnification ##################
    Calculated pixel size: 198.5 +/- 0.3 A/pix (n= 11).
    This difference of 1 % from the current 196.3 A/pix value.
    ############################################################

The new values of pixel size can then be changed in the :code:`SerialEMProperties.txt` in RotationAndPixel section as follows:

The example assumes that magnification 62x is used for the atlas magnification:

.. code-block::
    
    #Initial settings
    RotationAndPixel  4   -1.8  999   64.42   # 62

    #After refinement
    RotationAndPixel  4   -1.8  999   65.54   # 62 Changed from 64.42 on YYYYMMDD

.. note:: SerialEM needs to be restarted after modifying the properties file.
        
