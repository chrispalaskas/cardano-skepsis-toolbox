{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = inputs:
    inputs.flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = inputs.nixpkgs.legacyPackages.${system};
        my-python = pkgs.python3;
        python-with-my-packages = my-python.withPackages (p: with p; [
          wheel
          requests
          # other python packages you want
        ]);
      in
      {
        devShell =
          pkgs.mkShell
            {
              buildInputs = [
                python-with-my-packages
              ];
              shellHook = ''
                PYTHONPATH=${python-with-my-packages}/${python-with-my-packages.sitePackages}
                # maybe set more env-vars
              '';
            };
      }
    );
}

