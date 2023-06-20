"""
run_qmrebind_amber.py

Run qmrebind for Amber inputs. Qmrebind reparametrizes the partial charges
on atoms using a QMMM ONIOM calculation on the ligand in the bound state of
the receptor.
"""
import os
import shutil
import argparse

import qmrebind
import defaults

# TODO: rename cut_off_distance to qm2_cutoff_distance
def run_qmrebind_amber(
        input_pdb, forcefield_file, ligand_resname, cut_off_distance=3.0,
        nprocs=1, maxiter=2000, qm_method="B3LYP", qm_basis_set="6-311G",
        qm_charge_scheme="CHELPG", qm_charge=0, qm_mult=1, qm2_method="XTB", 
        qm2_charge_scheme="CHELPG", qm2_charge=0, qm2_mult=1, 
        orca_dir_pwd=None, work_dir=None):
        
    if orca_dir_pwd is None:
        orca_path = shutil.which("orca")
        orca_dir_pwd = os.path.dirname(orca_path)
        print("Using ORCA at:", orca_path)
    
    qmrebind.make_work_dir([input_pdb, forcefield_file], work_dir)
    
    # TODO: Remove work "simulation" - rename to "calculation"
    # Getting started with the ORCA simulation using the modified intial PDB 
    # file
    
    qmrebind.prepare_pdb(input_pdb=input_pdb)
    
    qmrebind.strip_topology(forcefield_file=forcefield_file)
    
    qmrebind.get_system_charge(
        forcefield_file=forcefield_file, input_pdb=input_pdb)
    
    qmrebind.get_ligand_pdb(
        input_pdb=input_pdb, ligand_pdb=defaults.ligand_pdb, 
        ligand_resname=ligand_resname)
    
    qmrebind.get_receptor_pdb(
        input_pdb=input_pdb, receptor_pdb=defaults.receptor_pdb, 
        ligand_resname=ligand_resname)
    
    qm_region_atom_indices = qmrebind.get_indices_qm_region(
        input_pdb=input_pdb, ligand_resname=ligand_resname)
    print(f"The indices for the atoms in the QM region are: "
          f"{qm_region_atom_indices}, and the number of atoms is: "
          f"{len(qm_region_atom_indices)}.")
    
    # TODO: consolidate to more efficient. Reduce to single var
    qm2_region_residue_indices, qm2_region_atom_indices \
        = qmrebind.get_indices_qm2_region(
            ligand_pdb=defaults.ligand_pdb, receptor_pdb=defaults.receptor_pdb, 
            cut_off_distance=cut_off_distance)
    print(f"The indices for atoms in the QM2 region are: "
          f"{qm2_region_atom_indices}, and the number of atoms are: "
          f"{len(qm2_region_atom_indices)}.")
    print(f"The indices for residues in the QM2 region are: "
          f"{qm2_region_residue_indices}, and the number of atoms are: "
          f"{len(qm2_region_residue_indices)}.")
    
    qmrebind.prepare_orca_pdb(
        input_pdb=input_pdb,
        ligand_pdb=defaults.ligand_pdb,
        orca_pdb=defaults.orca_pdb,
        ligand_resname=ligand_resname,
        receptor_pdb=defaults.receptor_pdb,
        cut_off_distance=cut_off_distance,
    )
    
    qmrebind.get_amber_to_orca_prms(forcefield_file=forcefield_file)
    
    # TODO: is it really an ORCA simulation? Would it be called a calculation?
    # ORCA simulation
    
    qmrebind.get_orca_input(
        nprocs=nprocs,
        maxiter=maxiter,
        qm_method=qm_method,
        qm_basis_set=qm_basis_set,
        qm2_method=qm2_method,
        optimization=defaults.optimization,
        frequency_calculation=defaults.frequency_calculation,
        qm_charge_scheme=qm_charge_scheme,
        qm2_charge_scheme=qm2_charge_scheme,
        qm2_charge=qm2_charge,
        qm2_mult=qm2_mult,
        forcefield_file=forcefield_file,
        input_pdb=input_pdb,
        ligand_resname=ligand_resname,
        orca_pdb=defaults.orca_pdb,
        orca_input_file=defaults.orca_input_file,
        ligand_pdb=defaults.ligand_pdb,
        receptor_pdb=defaults.receptor_pdb,
        cut_off_distance=cut_off_distance,
        qm_charge=qm_charge,
        qm_mult=qm_mult,
    )
    
    """ # TODO: marked for removal
    add_xtb_inputs(
        etemp=etemp,
        solvation=solvation,
        solvent=solvent,
        accuracy=accuracy,
        xtb_memory=xtb_memory,
        xtb_nprocs=xtb_nprocs,
        orca_input_file=orca_input_file,
        XTB_add_inputs=XTB_add_inputs,
    )
    """
    qmrebind.run_orca_qmmm(
        orca_dir_pwd=orca_dir_pwd,
        orca_input_file=defaults.orca_input_file,
        orca_out_file=defaults.orca_out_file,
    )
    
    # Post simulation
    
    qmrebind.get_qm_charges(
        orca_out_file=defaults.orca_out_file,
        qm_charge_file=defaults.qm_charge_file,
        input_pdb=input_pdb,
        ligand_resname=ligand_resname,
        qm_charge_scheme=qm_charge_scheme,
    )
    
    qmrebind.get_ff_charges(
        forcefield_file=forcefield_file,
        ff_charges_file=defaults.ff_charges_file,
        input_pdb=input_pdb,
    )
    
    qmrebind.get_ff_qm_charges(
        qm_charge_file=defaults.qm_charge_file,
        ff_charges_file=defaults.ff_charges_file,
        ff_charges_qm_fmt_file=defaults.ff_charges_qm_fmt_file,
        input_pdb=input_pdb,
        ligand_resname=ligand_resname,
    )

    qmrebind.get_qmrebind_parm(
        forcefield_file=forcefield_file,
        input_pdb=input_pdb,
        ff_charges_qm_fmt_file=defaults.ff_charges_qm_fmt_file,
    )
    
    # Post Analysis
    
    qmrebind.get_qmrebind_parm_solvent(
        input_pdb=input_pdb,
        forcefield_file=forcefield_file,
        ff_charges_file=defaults.ff_charges_file,
    )
    
    qmrebind.get_energy_diff_no_solvent(
        forcefield_file=forcefield_file, input_pdb=input_pdb)
    
    qmrebind.get_energy_diff_solvent(
        forcefield_file=forcefield_file, input_pdb=input_pdb)
    
    qmrebind.rename_receptorligand_pdb(input_pdb=input_pdb)
    
    qmrebind.run_openmm_sim(
        input_pdb=input_pdb, forcefield_file=forcefield_file, 
        sim_steps=defaults.sim_steps, T=defaults.T
    )
    
    qmrebind.get_charge_diff_file(
        forcefield_file=forcefield_file,
        ligand_pdb=defaults.ligand_pdb,
        ligand_charge_diff_file=defaults.ligand_charge_diff_file,
    )
    
    qmrebind.get_log_files(
        orca_pdb=defaults.orca_pdb,
        orca_input_file=defaults.orca_input_file,
        orca_out_file=defaults.orca_out_file,
        receptor_pdb=defaults.receptor_pdb,
        ligand_pdb=defaults.ligand_pdb,
    )

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        "input_pdb", metavar="INPUT_PDB", type=str,
        help="The PDB file of the system to be reparametrized. The PDB file "\
        "defines the atomic positions of the system. It also must contain "\
        "box vector information in the form of a CRYST line.")
    argparser.add_argument(
        "forcefield_file", metavar="FORCEFIELD_FILE", type=str, 
        help="The name of the forcefield file whose atomic point charges "\
        "will be refined. For the AMBER forcefield, this would be a .parm7 "\
        "or a .prmtop file.")
    argparser.add_argument(
        "ligand_resname", metavar="LIGAND_RESNAME", type=str, 
        help="The 3-letter residue name for the ligand, which will comprise "\
        "the QM region of the system in the ONIOM calculation.")
    argparser.add_argument(
        "-c", "--cut_off_distance", dest="cut_off_distance", default=3.0,
        help="The cut-off distance (in Angstroms) used to define the QM2 "\
        "region of the ONIOM calculation.", type=float)
    argparser.add_argument(
        "-n", "--nprocs", dest="nprocs", default=1,
        help="The number of processors to use for ORCA calculations.", 
        type=int)
    argparser.add_argument(
        "-i", "--max_iterations", dest="max_iterations", default=2000,
        help="The maximum number of iterations for ORCA convergence.", 
        type=int)
    argparser.add_argument(
        "-m", "--qm_method", dest="qm_method", default="B3LYP",
        help="The method to use for the QM region of the ONIOM calculation. "\
        "Please see the file orca_methods_basis_sets.pdf for all possible "\
        "options.", type=str)
    argparser.add_argument(
        "-b", "--qm_basis_set", dest="qm_basis_set", default="6-311G",
        help="The basis set to use for the QM region of the ONIOM "\
        "calculation. Please see the file orca_methods_basis_sets.pdf for all "\
        "possible options.", type=str)
    argparser.add_argument(
        "-s", "--qm_charge_scheme", dest="qm_charge_scheme", default="CHELPG",
        help="The charge scheme to use for the QM region of the ONIOM "
        "calculation. Please see the file orca_methods_basis_sets.pdf for all "\
        "possible options.", type=str)
    argparser.add_argument(
        "-q", "--qm_charge", dest="qm_charge", default=0,
        help="The total charge of the QM region of the ONIOM calculation.",
        type=int)
    argparser.add_argument(
        "-u", "--qm_multiplicity", dest="qm_multiplicity", default=1,
        help="The multiplicity of the QM region of the ONIOM calculation.",
        type=int)
    argparser.add_argument(
        "-M", "--qm2_method", dest="qm2_method", default="XTB",
        help="The method to use for the QM2 region of the ONIOM calculation. "\
        "Please see the file orca_methods_basis_sets.pdf for all possible "\
        "options.", type=str)
    argparser.add_argument(
        "-S", "--qm2_charge_scheme", dest="qm2_charge_scheme", default="CHELPG",
        help="The charge scheme to use for the QM2 region of the ONIOM "
        "calculation. Please see the file orca_methods_basis_sets.pdf for all "\
        "possible options.", type=str)
    argparser.add_argument(
        "-Q", "--qm2_charge", dest="qm2_charge", default=0,
        help="The total charge of the QM2 region of the ONIOM calculation.",
        type=int)
    argparser.add_argument(
        "-U", "--qm2_multiplicity", dest="qm2_multiplicity", default=1,
        help="The multiplicity of the QM2 region of the ONIOM calculation.",
        type=int)
    argparser.add_argument(
        "-o", "--orca_path", dest="orca_path", default=None,
        help="An absolute path to the ORCA program. If not specified, ORCA "\
        "will be found from the shutil.which() command.", type=str)
    argparser.add_argument(
        "-w", "--work_dir", dest="work_dir", default=None,
        help="A working directory for all temporary files, log files, etc.", 
        type=str)
    
    args = argparser.parse_args()
    args = vars(args)
    input_pdb = args["input_pdb"]
    forcefield_file = args["forcefield_file"]
    ligand_resname = args["ligand_resname"]
    cut_off_distance = args["cut_off_distance"]
    nprocs = args["nprocs"]
    max_iterations = args["max_iterations"]
    qm_method = args["qm_method"]
    qm_basis_set = args["qm_basis_set"]
    qm_charge_scheme = args["qm_charge_scheme"]
    qm_charge = args["qm_charge"]
    qm_multiplicity = args["qm_multiplicity"]
    qm2_method = args["qm2_method"]
    qm2_charge_scheme = args["qm2_charge_scheme"]
    qm2_charge = args["qm2_charge"]
    qm2_mult = args["qm2_multiplicity"]
    orca_path = args["orca_path"]
    work_dir = args["work_dir"]
    
    run_qmrebind_amber(
        input_pdb, forcefield_file, ligand_resname, 
        cut_off_distance=cut_off_distance, nprocs=nprocs, 
        maxiter=max_iterations, qm_method=qm_method, qm_basis_set=qm_basis_set,
        qm_charge_scheme=qm_charge_scheme, qm_charge=qm_charge, 
        qm_mult=qm_multiplicity, qm2_method=qm2_method, 
        qm2_charge_scheme=qm2_charge_scheme, qm2_charge=qm2_charge, 
        qm2_mult=qm2_mult, orca_dir_pwd=orca_path, work_dir=work_dir)