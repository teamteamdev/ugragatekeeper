{
  description = "Bot for keeping order in your Telegram chat";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    poetry2nix.url = "github:nix-community/poetry2nix";
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      overlays.default = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          moderator = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;

            postInstall = ''
              install -Dm644 config-clean.yaml $out/etc/moderator.yaml
            '';
          };
        })
      ];

      nixosModules = [
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
          drv = pkgs.moderator;
        };
      in
      {
        packages = {
          moderator = pkgs.moderator;
          default = pkgs.moderator;
        };

        apps = {
          moderator = app;
          default = app;
        };
      }));
}
