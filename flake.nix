{
  description = "Bot for keeping order in your Telegram chat";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
    poetry2nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    poetry2nix,
  }:
    {
      overlays.default = final: prev: {
        ugragatekeeper = final.poetry2nix.mkPoetryApplication {
          python = final.python311;
          projectDir = ./.;
          overrides = final.poetry2nix.defaultPoetryOverrides.extend (final: prev: {
            aiogram = prev.aiogram.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or []) ++ [final.setuptools];
            });
          });
        };
      };

      nixosModules.default.imports = [
        (import ./module.nix self.packages)
      ];
    }
    // (flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [poetry2nix.overlays.default self.overlays.default];
      };

      app = flake-utils.lib.mkApp {
        drv = pkgs.ugragatekeeper;
      };
    in {
      packages = {
        ugragatekeeper = pkgs.ugragatekeeper;
        default = pkgs.ugragatekeeper;
      };

      apps = {
        ugragatekeeper = app;
        default = app;
      };

      formatter = pkgs.alejandra;
    }));
}
