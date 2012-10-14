#SeeDash a CLI to CDash.

See quickly what is wrong with your dashboard,

####Examples:

Find failures in the vtk nightly

    seedash VTK

List all projects you can search

    seedash dashboards

List all errors in the vtk nightly expected

    seedash VTK --group "Nightly Expected"


List all errors in the paraview nightly next

    seedash ParaView --group "Nightly (next)"

Find failure in the vtk nightly and list developers that modified
code per test that might have caused the failure

    seedash VTK --with-devs

####Features to do:

Find failures and warnings in paraview nightly

    seedash ParaView --warnings



Show only warnings

     seedash ParaView --no-errors --warnings





