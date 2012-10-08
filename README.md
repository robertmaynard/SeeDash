SeeDash a CLI to CDash.

See quickly what is wrong with your dashboard,

Examples:

Find failures in the vtk nightly

  seedash VTK

List all projects you can search

  seedash dashboards

List all errors in the vtk nightly expected

seedash.py VTK --group "Nightly Expected"


List all errors in the paraview nightly next

seedash.py ParaView --group "Nightly (next)"

#Features to do:

Find failures and warnings in paraview nightly

seedash ParaView --warnings

Find failure in the vtk nightly you might be part of

seedash VTK --user UserName

Show only warnings

seedash ParaView --no-errors --warnings





