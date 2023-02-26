{
  description = "Bot for keeping order in your Telegram chat";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    {
      overlays.default = final: prev: {
        ugragatekeeper = final.poetry2nix.mkPoetryApplication {
          python = final.python310;
          projectDir = ./.;
          overrides = final.poetry2nix.defaultPoetryOverrides.extend (final: prev: {
            aiogram = prev.aiogram.overridePythonAttrs (old: {
              buildInputs = (old.buildInputs or [ ]) ++ [ final.setuptools ];
            });
          });
        };
      };

      nixosModules.default.imports = [
        ({ pkgs, ... }: {
          nixpkgs.overlays = [ self.overlays.default ];
        })
        (import ./module.nix)
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        };

        app = flake-utils.lib.mkApp {
          drv = pkgs.ugragatekeeper;
        };
      in
      {
        packages = {
          ugragatekeeper = pkgs.ugragatekeeper;
          default = pkgs.ugragatekeeper;
        };

        apps = {
          ugragatekeeper = app;
          default = app;
        };
      }));
}
